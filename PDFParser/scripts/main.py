"""
    Author: Azatot

    Description:
        The main purpose of the script is to find a directory with PDFs files and extract: 
            Product name, Company name, and Company email from there.

        There are many occurrences of a "Product name" in different sequences, 
            so the DICTIONARY "sequences" have the most common a
                nd frequent RegEX expressions to extract the data.

        Actually, a "Product name" is the most difficult part as it may appear on different pages and in a different order. 
            Since that, there are 3 different functions to search for a "Product name".

        It is more reasonable to search for "Company name" and "Email" only after a "Product name" is found, 
            otherwise, it may be waste of time and resources.

        At some points, the code is getting messy, however, 
            the most efficient algorithm might not work for such kind of structure of PDFs.

        Steps of execution:
            1. Get the Product name by:
                1.1 The PRODUCT NAME template
                1.2 The TRADE NAME template
                1.3 The PRODUCT INDENTIFIER template
                1.4 The NAME OF PRODUCT template
            
            2. Get the Company name by:
                2.1 The DETAILS OF THE SUPPLIER template
                2.2 The MANUFACTURER template
                2.3 The COMPANY NAME
                2.4 The SUPPLIER template

            3. Get the Email of the company
"""

import os
import re
import csv
import fitz
import pathlib
from re_templates import product_name_templates, company_name_templates, email_templates



PATH = pathlib.Path(__file__).parent
DIRECTORIES = os.listdir(str(PATH.parent))
PDF_DIRECTORY = None

for dr in DIRECTORIES:
    if '.' not in dr and 'cache' not in dr:

        PDF_DIRECTORY = dr
        break

with open(str(PATH.parent) + '/uncatched_words.txt', 'r') as grb:
    garbage = tuple(word.strip('\n') for word in grb.readlines())

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


def main(pdf_path):
    """
        The entry point of the script to execute all other function and check its outputs.
    """
    with fitz.Document(pdf_path) as document:
        page = document.load_page(0)
        pg_text = page.get_text()

        pn = product_name_finder(pg_text)
        comp_name = company_name_finder(pg_text)
        email = find_email(pg_text)

        try:
            if not pn:
                print(pdf_path)
                print(repr(pg_text))
                print('-'*90)
                page = document.load_page(1)
                pg_text = page.get_text()
                pn = product_name_finder(pg_text)

            if not comp_name:
                page = document.load_page(1)
                pg_text = page.get_text()
                comp_name = company_name_finder(pg_text)

            if not email:
                page = document.load_page(1)
                pg_text = page.get_text()
                email = find_email(pg_text)


        except ValueError:
            pass

        file_name = pdf_path.split('/')[-1]

        if pn and pn not in garbage and comp_name and comp_name not in garbage and email:
            return file_name, pn, comp_name, email



if __name__ == "__main__":
    if PDF_DIRECTORY:

        PDF_FILES = os.listdir(str(PATH.parent) + '/' + PDF_DIRECTORY)

        with open(str(PATH.parent) + '/output.csv', 'w') as file:
            csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(('File name', 'Product name', 'Company name', 'Email'))

            for PDF in PDF_FILES:
                PDF_PATH = f'{str(PATH.parent)}/{PDF_DIRECTORY}/{PDF}'
                try:
                    success = main(PDF_PATH)
                    if success:
                        csv_writer.writerow(success)
                except RuntimeError:
                    print()
                    print(f'-----File {PDF} is corrupted!-----')
                    print()
    else:
        print()
        print('-----The folder with PDFs is NOT FOUND!-----')
        print()



