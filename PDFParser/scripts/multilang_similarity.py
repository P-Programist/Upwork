import os
import re
import sys
import csv
import ntpath

from string import punctuation

import fitz
import pathlib
import numpy as np
import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from rapidfuzz import fuzz
from re_templates import product_name_templates, company_name_templates, email_templates


# MuPDF is a bit over-verbosed on warnings.
# We only want to handle exceptions
fitz.TOOLS.mupdf_display_errors(False)
# For determenistic language prediction
DetectorFactory.seed = 0

PATH = pathlib.Path(__file__).parent

with open(str(PATH.parent) + '/uncatched_words.txt', 'r') as grb:
    garbage = tuple(word.strip('\n') for word in grb.readlines())

try:
    import ocrmypdf
    OCR_AVAILABLE = True  # Use OCR or skip files without text layer
except ImportError:
    print('OCR not available, please install OCRMyPDF (see README)')
    OCR_AVAILABLE = False

KEYLINES_FILENAME = f'{str(PATH.parent)}/Strings to identify SDS all languages v5.xlsx'
LINES_FOR_OCR = 30  # if less than this number of overall lines is found in text - OCR
MULTI_SDS_MIN_PAGE_COUNT = 25  # Minimum page count to treat PDF as multi SDS
PUNCTUATION = set(punctuation)  # basic punctuation special symbols
PUNCTUATION.remove('.')  # Often goes as alignment in agendas
# Stop condition Regexp: we are trying to find first Section 3 subsection, like:
# 3.1 substances, 3.2 mixtures, 3.2 chemical characterisation: mixtures and so on
# Regexp has to be strong to exclude false positive stops (tested on 3800 pdfs)
STOP_PATTERN = re.compile(r'3\.[12][\.\s]+[a-z]{5,}')


class InvalidTextError(Exception):
    '''Exception for empty/wrong language text layer document'''
    pass


def get_language(text):
    '''
    Determine language text.

    Also determine if record is basically a text:
    a lot of trash text layers are consist of punctuation mainly.
    '''
    # Punctuation ratio for given trash text
    if not len(text):
        return 'unknown'

    punct_ratio = len([c for c in text if c in PUNCTUATION]) / len(text)
    if punct_ratio > 0.5:
        return 'unknown'

    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return 'unknown'


def get_reference_data(file):
    '''
    Reference lines and Section 3 candidates for each available language.

    File notation for beginning of line:
    $ - helper_line. We use this line only for order metric, not distance metric.
        Also these lines are not relevant for short documents.
        Good examples are: UNCOMPLETE lines such as address, email, and so on

    Returns a tuple with:

    1. All keylines with needed metadata for each language
    2. Section 3 header candidates for each language
    '''
    def parse_line(line):
        '''Parsing line semantics'''

        helper_line = False
        line = line.lower()

        if line.startswith('$'):
            # only relevant for order score
            line = line.lstrip('$').strip()
            helper_line = True

        return {
            'line': line,
            'helper_line': helper_line
        }

    lines_df = pd.read_excel(file, sheet_name='string_list')
    lines = lines_df.groupby('lang_short').line.apply(lambda lines: [parse_line(ln) for ln in lines])

    section3_candidates_df = pd.read_excel(file, sheet_name='section3_candidates')
    section3_candidates = section3_candidates_df.groupby('lang_short').apply(
        lambda x: {ln: s for ln, s in zip(x.line, x.min_similarity)}
    )

    layout_markers_df = pd.read_excel(file, sheet_name='layout_markers')
    layout_markers = layout_markers_df.set_index('lang_short').to_dict(orient="index")
    return lines.to_dict(), section3_candidates.to_dict(), layout_markers


def get_document_data(file, min_length=5):
    '''
    Basic page-to-page text extraction,
    cleansing, and line splitting. Also returns all
    the document metadata needed
    '''
    try:
        meta = {}
        with fitz.open(file) as doc:
            meta['page_count'] = len(doc)
            lines = []

            for page in doc:
                page_text = page.get_text('text')

                # Cleansing
                page_text = page_text.lower()
                page_text = re.sub(r'[\*�]', '', page_text)  # artefacts of bad text layer
                for line_text in page_text.split('\n'):
                    line_text = line_text.replace('\t', ' ')
                    line_text = re.sub(r'\s+', ' ', line_text)

                    if len(line_text) < min_length:
                        # too short lines causes noise in similarity
                        continue

                    lines.append(line_text.strip())
    except RuntimeError as e:
        # Unfortunately there are no specific exceptions on corrupted file,
        # so we reraise with filename and MuPDF error text
        raise RuntimeError(f'Corrupted PDF: {file}, MuPDF says: {str(e)}')

    # All lines is needeed to scan for multi SDS
    meta['all_lines'] = lines
    relevant_lines = lines

    # Try to limit the search scope with section 3
    for i, line in enumerate(lines):
        # Specific stop condidion: if we reach section 3 subsections
        if STOP_PATTERN.match(line):
            relevant_lines = lines[:i]
            break

    return relevant_lines, meta


def get_candidate_lines(keylines, lines, meta):
    """
    For each key line get the candidate
    line from file lines with similarity metrics
    and line position
    """
    results = []

    # Heuristic 1: limit the search scope with the best candidate
    # for the LAST reference line
    last_line_candidates = []

    # Find the best candidate
    for position, line in enumerate(lines):
        similarity = fuzz.ratio(keylines[-1]['line'], line)
        last_line_candidates.append((similarity, position, line))

    cand_score, cand_pos, cand_line = max(last_line_candidates)

    # if it is not a random match (at least 55%)
    # and it cointains number "3", limit the search scope
    # (because in rare cases sections 2 and 3 are swapped)
    if (cand_score > 55 and '3' in cand_line):
        search_scope = lines[:cand_pos + 1]  # +1 because the line itself is very valuable for matching
    else:
        search_scope = lines

    # Heuristic 2: for very short documents (2-5 pages)
    # there often will be only sections with brief info
    # no adresses and detailed descriptions,
    # so we dont take some lines into account
    if 1 < meta['page_count'] < 5:
        keyline_scope = [kl for kl in keylines if not kl['helper_line']]
    else:
        keyline_scope = keylines

    # Now pick the best candidate for each reference line
    for keyline in keyline_scope:
        candidates = []

        for position, line in enumerate(search_scope):
            similarity = fuzz.ratio(keyline['line'], line)
            candidates.append({
                'line': line,
                'similarity': similarity,
                'position': position
            })

        best_match = max(candidates, key=lambda c: c['similarity'])
        results.append({'keyline': keyline, **best_match})

    return results

def get_pdf_strings(file, type, start, stop, min_length=5):
    stoppattern = ""
    startptrn =""
    sec2ptrn = r'(((2)?(\s.\s)?(\:)?(\.)?(\s+)?Hazards\sidentification)|(TRANSPORTATION\sINFORMATION))'
    if type == 1:
        stoppattern = r'(1\.2(\.)?)?(\s+)?(Relevant\sidentified(.+)(\s)|Product\sUses|^SUPPLIER)'
    elif type == 2 or type == 3:
        startptrn = r'((Details\sof\sthe\ssupplier(\s+))|(NAME\sOF\sMANUFACTURER/SUPPLIER))'
        stoppattern = r'(1\.4)(\.)?(\s+)?(Emergency\stelephone\snumber)'

    contents = ""
    email = ""
    try:
        with fitz.open(file) as doc:
            if stop is not True:
                for page in doc:
                    page_blocks = page.get_text('blocks')
                    page_blocks.sort(key=lambda block: block[1])
                    # Extracting text:
                    if stop is not True:
                        for block in page_blocks:
                            block_type = block[6]
                            if block_type == 1:  # ignore image blocks
                                continue
                            block_text = block[4]

                            section1_3 = re.search(startptrn, block_text, re.IGNORECASE)
                            if section1_3 is not None:
                                start = True
                            if type == 1:
                                contents += block_text
                            elif type == 2 or type == 3:
                                if start == True:
                                    contents += block_text
                            section2 = re.search(sec2ptrn, block_text, re.IGNORECASE)
                            section1_2 = re.search(stoppattern,block_text, re.IGNORECASE|re.MULTILINE)
                            if section2 is not None or section1_2 is not None:
                                stop = True
                                break

    except RuntimeError as e:
        # Unfortunately there are no specific exceptions on corrupted file,
        # so we reraise with filename and MuPDF error text
        raise RuntimeError(f'Corrupted PDF: {file}, MuPDF says: {str(e)}')

    if start is False:
        contents = get_pdf_strings(file, type, True, False)

    return contents


def re_constructor(sequence, text, ignore_case=True):
    """
        The functions gets 2 parameters to make the search by the template
    """
    if ignore_case:
        template = re.compile(sequence, re.IGNORECASE)
    else:
        template = re.compile(sequence)

    result = re.search(template, text)

    return result


def product_name_finder(page_text):
    """
        The function get the PDF text and applies RegEX templates 
            from sequences dictionary to find "product_name"
    """
    if not page_text:
        return None

    for re_template in product_name_templates:
        product_name_re = re_constructor(re_template, page_text)

        if product_name_re:
            text = product_name_re.group(0).strip().split(':')

            if len(text) == 1:
                product_name = text[0].strip('\n').split('\n')[-1].strip()
                if product_name and product_name not in garbage:
                    return product_name
    
            elif len(text) == 2:
                product_name = text[1].strip('\n').split('\n')[-1].strip()
                if product_name and product_name not in garbage:
                    return product_name

            elif len(text) == 3:
                product_name1 = text[1].strip('\n').strip()
                
                if product_name1 not in garbage:
                    product_name = product_name1.split('\n')

                    if product_name[0].strip() not in garbage:
                        return product_name[0].strip()

                    elif product_name[-1].strip() not in garbage:
                        return product_name[-1].strip()

                else:
                    if text[-1] and text[-1].strip() not in garbage:
                        return text[-1].strip()
           
            else:
                product_name = text[2].strip('\n').strip().split('\n')

                if product_name[0] not in garbage and len(product_name[0]) > 3:
                    return product_name[0].strip()
            break
    

def company_name_finder(page_text):
    """
        The function tries to find the company name based on RegEX templates 
            from sequences dictionary
    """
    if not page_text:
        return None

    for re_template in company_name_templates:

        company_name_v0 = re_constructor(re_template, page_text)

        if company_name_v0:
            company_name = company_name_v0.group(0).strip('\n').split(':')

            if len(company_name) == 1:
                cn = company_name[0].strip().split('\n')
                if cn[-1] not in garbage:
                    return cn[-1].strip()

            elif len(company_name) == 2:
                if company_name[-1] and company_name[-1].strip('\n').strip():
                    cn = company_name[-1].strip('\n').strip()
                    return cn

            elif len(company_name) == 3:
                cn = company_name[-1].strip().replace('\n', '').strip()
                if cn and cn not  in garbage:
                    return cn
                
            else:
                if company_name[-1] and company_name[-1].strip() not  in garbage:
                    return company_name[1].strip()
            break


def find_email(page_text):
    """
        The function tries to find the company email based on RegEX templates 
            from sequences dictionary
    """

    if not page_text:
        return None

    for em in email_templates:

        email_v0 = re_constructor(em, page_text)

        if email_v0:
            extracted_text_v0 = email_v0.group(0).strip()

            if ':' in extracted_text_v0:
                email = extracted_text_v0.split(':')[-1].strip()
                return email
            else:
                email = extracted_text_v0.strip()
                return email


def get_comparison_lists(results):
    """
    Helper function to split similarity function results
    into two lists:
        :keylines_with_candidates: keylines from candidate search in their truthy order
        :ordered_keylines: same keylines in order their most similar candidate line
            appear in the document
    """
    keylines_with_candidates = [result['keyline']['line'] for result in results]

    ordered_keylines = [
        result['keyline']['line']
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


def is_ocr_needed(lines, doc_text, language, layout_markers):
    '''Attempt to determine if OCR needed with all the heuristics'''
    # Wrong language usually means broken text layer

    if language not in layout_markers:
        return True

    # Section 3 stands earlier in the document than Section 1
    # This is also a sign of a bad text layer with wrong orderiing
    main_marker = layout_markers[language]['main_marker']
    section_name = layout_markers[language]['section_name']
    broken_layout = False

    if main_marker in doc_text:
        if -1 < doc_text.find(f'{section_name} 3') < doc_text.find(f'{section_name} 1'):
            broken_layout = True

    # Combine conditions together
    ocr_condition = (
        len(lines) < LINES_FOR_OCR or  # too few lines
        broken_layout
    )
    return ocr_condition


def process(pdf_file, keylines, section3_candidates, layout_markers, use_ocr=True):
    '''Main processing function'''
    product_name = ""
    lines, meta = get_document_data(pdf_file)


    # Main OCR condidtion: too few lines or not an english text

    doc_text = ''.join(lines)
    language = get_language(doc_text)

    if is_ocr_needed(meta['all_lines'], doc_text[:15000], language, layout_markers):
        if OCR_AVAILABLE and use_ocr:
            # quite a bit of time (may take minutes per file)
            # OCR file inplace and process it again
            print('Not enough text or not english or broken text, starting OCR')
            try:
                ocrmypdf.ocr(pdf_file, pdf_file, force_ocr=True, deskew=False, optimize=0, output_type='pdf')  # noqa
                return process(pdf_file, keylines, section3_candidates, layout_markers, use_ocr=False)
            except Exception as e:
                print(f'OCR failed with error: {str(e)}, results may be poor')
        else:
            raise InvalidTextError(f'File {pdf_file} needs OCR, not enough text or bad text/layout')

    # After OCR is done, we get language specific reference data and start the matching
    # If inferred language doesnt match our set - raise exception
    try:
        specific_keylines = keylines[language]
        specific_section3_candidates = section3_candidates[language]
        specific_section3_anchor = layout_markers[language]['section3_anchor']
    except KeyError:
        raise InvalidTextError(f'File {pdf_file} has invalid language: {language}')

    candidates = get_candidate_lines(specific_keylines, lines, meta)
    mean_distance = np.mean([
        cand['similarity'] for cand in candidates
        if not cand['keyline']['helper_line']
    ])
    order_score = calc_order_score(*get_comparison_lists(candidates))
    final_score = (order_score + mean_distance) / 2
    sds_count = get_possible_sds_count(
        final_score, meta, specific_section3_candidates, specific_section3_anchor
    )

    product_name = product_name_finder(doc_text[:15000])
    company_name = company_name_finder(doc_text[:15000])
    email = find_email(doc_text[:15000])


    special_char_file = open(f"{str(PATH.parent)}/special_characters_not_to_trim.txt", "r+")
    special_char_list = special_char_file.readlines()
    special = ""
    for f in special_char_list:
        line = re.sub(r"\n","",f)
        special += line

    product_name_trimmed = re.sub(r"[^\w " + special + "]+", '', product_name, flags=re.UNICODE)
    product_name_trimmed = re.sub(' +', ' ', product_name_trimmed)

    company_name_trimmed = re.sub(r"[^\w " + special + "]+", '', company_name, flags=re.UNICODE)
    company_name_trimmed = re.sub(' +', ' ', company_name_trimmed)

    product_file = open(f"{str(PATH.parent)}/product_exclusion_list.txt", "r+")
    product_exclusion_list = product_file.readlines()
    product_exclustion_similarity = 0
    for f in product_exclusion_list:
        line = re.sub(r"\n","",f)
        ratio = round(fuzz.ratio(line, product_name_trimmed) / 100, 1)
        if ratio > product_exclustion_similarity:
            product_exclustion_similarity = ratio

    company_file = open(f"{str(PATH.parent)}/companyname_exclusion_list.txt", "r+")
    company_exclusion_list = company_file.readlines()
    company_exclustion_similarity = 0
    email_exclustion_similarity = 0
    for f in company_exclusion_list:
        line = re.sub(r"\n", "", f)
        ratio = round(fuzz.ratio(line, company_name_trimmed) / 100, 1)
        if ratio > company_exclustion_similarity:
            company_exclustion_similarity = ratio
        ratio_email = round(fuzz.ratio(line, email) / 100, 1)
        if ratio_email > email_exclustion_similarity:
            email_exclustion_similarity = ratio

    df = pd.read_csv(f'{str(PATH.parent)}/master_result_extracted_data.csv')
    product_name_similarity = 0
    company_name_similarity = 0
    email_similarity = 0

    for i, j in df.iterrows():
        for k in j:
            if k == ntpath.basename(pdf_file):
                prod = str(j[1])
                comp = str(j[2])
                mail = str(j[3])
                product_name_similarity = round(fuzz.ratio(prod, product_name_trimmed) / 100, 1)
                company_name_similarity = round(fuzz.ratio(comp, company_name_trimmed) / 100, 1)
                email_similarity = round(fuzz.ratio(mail, email) / 100, 1)


    return {
        'file': ntpath.basename(pdf_file),
        'language':language,
        'Product_name': product_name,
        'Product_name_trimed':product_name_trimmed,
        'similarity_productnamemost_similar_string_in_product_exclusion_list':product_exclustion_similarity,
        'similarity_productname_master_result_extracted_data': product_name_similarity,
        'Company_name' : company_name,
        'Company_name_trimmed': company_name_trimmed,
        'similarity_companyname_most_similar_string_in_company_exclusion_list': company_exclustion_similarity,
        'similarity_companyname_master_result_extracted_data': company_name_similarity,
        'email' : email,
        'similarity_email_most_similar_string_in_companyname_exclusion_list': email_exclustion_similarity,
        'similarity_email_master_result_extracted_data':email_similarity,
        'order_score': order_score,
        'mean_distance': mean_distance,
        'final_score': final_score,
        'sds_count': sds_count,
    }


def get_possible_sds_count(final_score, meta, last_section_candidates, section3_anchor):
    '''
    Main desicion function.

    Possible SDS/NON SDS calculation and attempt to count concatenated SDSs
    inside big files.

    For relatively huge docs with proper final score lets count probable SDS count.
    We assume these docs as concatenated multi SDS files.
    Approach is simple: count top candidates for last (most representative) keyline
    with really high similarity. As this line can vary,
    we match against several candidates.
    '''
    if final_score < 45:
        # Basic NON SDS Case
        sds_count = 0
    elif final_score >= 45 and meta['page_count'] < MULTI_SDS_MIN_PAGE_COUNT:
        sds_count = 1
    elif final_score >= 45 and meta['page_count'] >= MULTI_SDS_MIN_PAGE_COUNT:
        sds_count = 0  # Because we count all SDSs here
        for position, line in enumerate(meta['all_lines']):
            if section3_anchor in line:
                for candidate_line, min_similarity in last_section_candidates.items():
                    similarity = fuzz.ratio(candidate_line, line)
                    if similarity > min_similarity:
                        # Special cases for bad (but very similar) lines:
                        # Doesnt have quotes in them:
                        # INVALID LINE EXAMPLE: 5.1.3 sds section 3 "composition/information on ingredients"
                        # Doesnt start with specific symbols, like "(" or
                        # "1" (because "11" can be a bad OCR of double quote)
                        # INVALID LINE EXAMPLE: (composition/information on ingredients) .
                        bad_line = (line[0] in ['(', '1']) or ('"' in line)

                        if not bad_line:
                            sds_count += 1
                            continue  # Dont test a line anymore if already matched

        # Edge cases: ratio between page count and sds count cant be very low
        # If we observe 1 or 2 pages per SDS - its definately a layout problem.
        # Good example: B74F61F216D24EB5ABBABA08101EABF6.ashx.pdf, which has
        # all secions repeated as agenda at each page
        if sds_count:
            if meta['page_count'] / sds_count <= 2:
                sds_count = 1

    return sds_count


def print_result(result):
    '''Prints result to console'''
    file = result['file']
    final_score = result['final_score']
    sds_count = result['sds_count']
    output = f'{file} {final_score:.2f}% SDS, {sds_count} possible SDSs detected'
    print(output)



if __name__ == '__main__':
    # This file keeps some words that passed through the filter and needed to be excluded
    # The "uncatched_words.txt" has to be next ti the script folder

    try:
        path = sys.argv[1]  # read file from command line
    except IndexError:
        print('Please enter PDF filenames PATH')
        exit()

    keylines, section3_candidates, layout_markers = get_reference_data(KEYLINES_FILENAME)

    PDFS = os.listdir(path)

    with open(str(PATH.parent) + '/output.csv', 'w') as file:
        csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(
            (
                'file','Product_name','Product_name_trimed',
                'similarity_productnamemost_similar_string_in_product_exclusion_list',
                'similarity_productname_master_result_extracted_data',
                'Company_name','Company_name_trimmed',
                'similarity_companyname_most_similar_string_in_company_exclusion_list',
                'similarity_companyname_master_result_extracted_data','email',
                'similarity_email_most_similar_string_in_companyname_exclusion_list',
                'similarity_email_master_result_extracted_data',
                'order_score','mean_distance','final_score','sds_count',
            )
        )
        for pdf in PDFS:
            print(PDFS.index(pdf), pdf)
            pdf = str(PATH.parent) + '/sds/' + pdf


            try:
                result = process(pdf, keylines, section3_candidates, layout_markers)

                csv_writer.writerow((
                    result.get('file'),
                    result.get('Product_name'),
                    result.get('Product_name_trimed'),
                    result.get('similarity_productnamemost_similar_string_in_product_exclusion_list'),
                    result.get('similarity_productname_master_result_extracted_data'),
                    result.get('Company_name'),
                    result.get('Company_name_trimmed'),
                    result.get('similarity_companyname_most_similar_string_in_company_exclusion_list'),
                    result.get('similarity_companyname_master_result_extracted_data'),
                    result.get('email'),
                    result.get('similarity_email_most_similar_string_in_companyname_exclusion_list'),
                    result.get('similarity_email_master_result_extracted_data'),
                    result.get('order_score'),
                    result.get('mean_distance'),
                    result.get('final_score'),
                    result.get('sds_count'),
                ))
            except Exception as e:
                print(f'Exception: {str(e)}')
                # exit()

        # print_result(result)


