import os
import re
import sys

import fitz
# MuPDF is a bit over-verbosed on warnings.
# We only want to handle exceptions
fitz.TOOLS.mupdf_display_errors(False)
import langid
import numpy as np

from rapidfuzz import fuzz

try:
    import ocrmypdf
    OCR_AVAILABLE = True  # Use OCR or skip files without text layer
except ImportError:
    print('OCR not available, please install OCRMyPDF (see README)')
    OCR_AVAILABLE = False

LINES_FOR_OCR = 5  # if less than this number of lines is found in text - OCR
KEYLINES_FILENAME = 'ordered list of strings that occurs in SDS.txt'
# Stop condition Regexp: we are trying to find first Section 3 subsection, like:
# 3.1 substances, 3.2 mixtures, 3.2 chemical characterisation: mixtures and so on
# Regexp has to be strong to exclude false positive stops (tested on 3800 pdfs)
STOP_PATTERN = re.compile(r'3\.[12][\.\s]+[a-z]{5,}')


class EmptyTextError(Exception):
    '''Exception for empty text layer document'''
    pass


def is_english(text):
    '''Check if text language is English'''
    return langid.classify(text)[0] == 'en'


def get_keylines(file):
    '''Reference lines list with logarithmic discount. Lowercased.'''
    with open(file, 'r') as f:
        lines = [line.lower() for line in f.read().splitlines()]
    return lines


def get_pdf_lines(file, min_length=5):
    '''
    Use fitz (pymupdf) for text layer extraction (x10-50 faster than pdfminer).

    Important extraction tip: the ordering (at least vertical) is crucial
    for metric quality. PDF inner design can vary a lot, aspecially with
    page footers. So it is important to extract text as it appears naturally
    on rendered page.

    MuPDF high-level text extraction ignores this, so we do it manually with
    blocks and its coordinates.

    MuPDF blocks has this structure:
        (x0, y0, x1, y1, content, _, type)

    type - 0 for text, 1 for image, we dont need images at that point

    :min_length - minimum length of string to be taken into account
    '''
    try:
        with fitz.open(file) as doc:

            lines = []

            for page in doc:
                page_blocks = page.get_text('blocks')

                # Sort blocks vertically
                page_blocks.sort(key=lambda block: block[1])

                # Extracting text:
                for block in page_blocks:
                    block_type = block[6]
                    if block_type == 1:  # ignore image blocks
                        continue

                    block_text = block[4]

                    # Cleansing
                    block_text = block_text.lower().strip()

                    for line_text in block_text.split('\n'):
                        line_text = line_text.replace('\t', ' ')
                        line_text = re.sub(r'\s+', ' ', line_text)

                        if len(line_text) < min_length:
                            continue

                        # stop condidion: if we reach section 3 subsections
                        if STOP_PATTERN.match(line_text):
                            return lines

                        lines.append(line_text)
    except RuntimeError as e:
        # Unfortunately there are no specific exceptions on corrupted file,
        # so we reraise with filename and MuPDF error text
        raise RuntimeError(f'Corrupted PDF: {file}, MuPDF says: {str(e)}')
    return lines


def get_candidate_lines(keylines, lines):
    """
    For each key line get the candidate
    lines from file lines with similarity metrics
    and line position

    :threshold - minimum distance for a candidate to be considered,
        but we also want a stronger threshold for shorter words

    Output result only contains the keylines that have a candidate over threshold
    """
    results = []

    for keyline in keylines:
        candidates = []

        for position, line in enumerate(lines):
            similarity = fuzz.ratio(keyline, line)
            candidates.append({
                'line': line,
                'similarity': similarity,
                'position': position
            })

        best_match = max(candidates, key=lambda c: c['similarity'])

        results.append({'keyline': keyline, **best_match})

    return results


def get_comparison_lists(results):
    """
    Helper function to split similarity function results
    into two lists:
        :keylines_with_candidates: keylines from candidate search in their truthy order
        :ordered_keylines: same keylines in order their most similar candidate line
            appear in the document
    """
    keylines_with_candidates = [result['keyline'] for result in results]

    ordered_keylines = [
        result['keyline']
        for result in sorted(results, key=lambda result: result['position'])
    ]
    return keylines_with_candidates, ordered_keylines


def calc_order_score(document_keylines, ordered):
    '''
    Levenstein distance approach on lists:
    Encode each element with single letter
    and calculate the distance
    '''
    mapping = {line: chr(i + 100) for i, line in enumerate(document_keylines)}

    document_keylines_decoded = ''.join([mapping[line] for line in document_keylines])
    ordered_decoded = ''.join([mapping[line] for line in ordered])
    return fuzz.ratio(document_keylines_decoded, ordered_decoded)


def process(pdf_file, keylines, use_ocr=True):
    '''Main processing function'''
    lines = get_pdf_lines(pdf_file)

    # Main OCR condidtion: too few lines or not an english text
    if (len(lines) < LINES_FOR_OCR) or not is_english(' '.join(lines)):
        if OCR_AVAILABLE and use_ocr:
            # quite a bit of time (may take minutes per file)
            # OCR file inplace and process it again
            print('Not enough text or not english, starting OCR')
            try:
                ocrmypdf.ocr(pdf_file, pdf_file, force_ocr=True, deskew=False, optimize=0, output_type='pdf')  # noqa
                return process(pdf_file, keylines, use_ocr=False)
            except Exception as e:
                print(f'OCR failed with error: {str(e)}, results may be poor')
        else:
            raise EmptyTextError(f'File {pdf_file} needs OCR, not enough text or bad text')

    candidates = get_candidate_lines(keylines, lines)
    mean_distance = np.mean([cand['similarity'] for cand in candidates])
    order_score = calc_order_score(*get_comparison_lists(candidates))

    return {
        'file': pdf_file,
        'order_score': order_score,
        'mean_distance': mean_distance,
    }


def print_result(result):
    '''Prints result to console'''
    file = result['file']
    order_score = result['order_score']
    mean_distance = result['mean_distance']
    output = f'{file} {order_score:.2f}% SDS, {mean_distance:.2f}% avg lines similarity'
    print(output)


if __name__ == '__main__':

    try:
        pdf = sys.argv[1]  # read file from command line
    except IndexError:
        print('Please enter PDF filename')
        exit()

    keylines = get_keylines(KEYLINES_FILENAME)

    try:
        result = process(pdf, keylines)
    except Exception as e:
        print(f'Exception: {str(e)}')
        exit()

    print_result(result)
