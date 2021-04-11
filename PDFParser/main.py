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


# The RegEX template expressions
sequences = {
    "pn_v0": r'Product name.*',
    "pn_v1": r'name.+\w+.*',
    "pn_v2": r' :?.*',
    "pn_v3": r'Product name.*\n.*\n.*',
    "pn_v4": r'\n.*\n',
    "pn_v5": r'\w+.*',
    "pn_v6": r'\n.*\n.*.?',
    "pn_v7": r'\w+.*',
    ##############################
    "tn_v0": r'e name.?\n.+\n.*',
    "tn_v1": r': \n?\w.*\W',
    "tn_v2": r'Trade name ?:.+\n?.*\n',
    "tn_v3": r':.*\n?',
    ##############################
    "pi_v0": r'Product identifier? \n?.*\n?',
    "pi_v1": r'\n.*\n',
    "pi_v2": r'Product identifier.*\n?.*\n?.*\n?.*',
    "pi_v3": r'\n.*\n.*\n',
    "pi_v4": r'name:?\n?.*',
    "pi_v5": r'name.?\n?.*\n?.*\n?.*\n',
    "pi_v6": r'\n\w+.*',
    ##############################
    "oth_v0": r'Name of product.?\n?\w.*\n',
    "oth_v1": r'\nProduct identifier:?.?\n.*\n.*',
    "oth_v2": r': \n?.*\n.*',
    "oth_v3": r'Trade name.*\n.*\n',
    ##############################
    "cn_v0_1": r'Details of the supplier',
    "cn_v0": r'Company name.?:.+',
    "cn_v1": r'Company name.*\n.*\n?.*',
    "cn_v2": r'\n.?Supplier.*\n.*\n.*',
    "cn_v3": r'.?Manufacturer.*\n.*\n.*',
    "cn_v4": r'Company\n.*\n.*',
    "cn_v5": r'Company.*\n.*\n.*',
    "cn_v6": r'Details of the supplier.*\n.*',
    ##############################
    "email_v0": r' .*@[A-Z.]+ ',
    "email_v1": r'\n.*@.*',
    "email_v2": r'.*@.*'
}


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
    product_name_v0 = re_constructor(sequences["pn_v0"], page_text)

    if product_name_v0:
        extracted_text_v0 = product_name_v0.group(0)
        product_name_v1 = re_constructor(sequences["pn_v1"], extracted_text_v0)

        if product_name_v1:
            extracted_text_v1 = product_name_v1.group(0)
            product_name_v2 = re_constructor(sequences["pn_v2"], extracted_text_v1)

            if product_name_v2:
                extracted_text_v2 = product_name_v2.group(0).replace(':', '').strip()
                return extracted_text_v2 if not extracted_text_v2.islower() else None


    product_name_v3 = re_constructor(sequences["pn_v3"], page_text)

    if product_name_v3:
        extracted_text_v3 = product_name_v3.group(0)
        product_name_v4 = re_constructor(sequences["pn_v4"], extracted_text_v3)

        if product_name_v4:
            extracted_text_v4 = product_name_v4.group(0).strip('\n').strip()
            product_name_v5 = re_constructor(sequences["pn_v5"], extracted_text_v4)
            
            if product_name_v5:
                extracted_text_v5 = product_name_v5.group(0).strip()
                return extracted_text_v5 if 'date of issue' not in extracted_text_v5.lower() else None
            else:
                product_name_v6 = re_constructor(sequences["pn_v6"], product_name_v3.group(0))

                if product_name_v6:
                    extracted_text_v6 = product_name_v6.group(0)
                    product_name_v7 = re_constructor(sequences["pn_v7"], extracted_text_v6)
                
                    if product_name_v7:
                        extracted_text_v7 = product_name_v7.group(0).strip()

                        if 'product' not in extracted_text_v7.lower() and\
                            'substance' not in extracted_text_v7.lower() and\
                            'trade' not in extracted_text_v7.lower():

                            return extracted_text_v7


def trade_name_finder(page_text):
    """
        The function get the PDF text and applies RegEX templates 
            from sequences dictionary to find "trade_name"
    """
    trade_name_v0 = re_constructor(sequences["tn_v0"], page_text)

    if trade_name_v0:
        extracted_text_v0 = trade_name_v0.group(0)
 
        trade_name_v1 = re_constructor(sequences["tn_v1"], extracted_text_v0)

        if trade_name_v1:
            extracted_text_v1 = trade_name_v1.group(0).replace('\n', '').replace(':', '').strip()
            return extracted_text_v1

    trade_name_v3 = re_constructor(sequences["tn_v2"], page_text)

    if trade_name_v3:
        extracted_text_v3 = trade_name_v3.group(0).strip()
        trade_name_v3 = re_constructor(sequences["tn_v3"], extracted_text_v3)

        if trade_name_v3:
            extracted_text_v3 = trade_name_v3.group(0).replace(': ', '').strip()
            return extracted_text_v3 if len(extracted_text_v3) > 3 else None


def product_identifier_finder(page_text):
    """
        The function get the PDF text and applies RegEX templates 
            from sequences dictionary to find "product_identifier"
    """
    product_identifier_v0 = re_constructor(sequences["pi_v0"], page_text)

    if product_identifier_v0:
        extracted_text_v0 = product_identifier_v0.group(0)
        product_identifier_v1 = re_constructor(sequences["pi_v1"], extracted_text_v0)

        if product_identifier_v1:
            extracted_text_v1 = product_identifier_v1.group(0)
            if 'Product' not in extracted_text_v1 and\
                    'name' not in extracted_text_v1.lower() and\
                        len(extracted_text_v1) > 3 and\
                            'mixture' not in extracted_text_v1.lower():

                return extracted_text_v1.replace('\n', '').strip()
    
    product_identifier_v2 = re_constructor(sequences["pi_v2"], page_text)

    if product_identifier_v2:
        extracted_text_v2 = product_identifier_v2.group(0)
        product_identifier_v3 = re_constructor(sequences["pi_v3"], extracted_text_v2)

        if product_identifier_v3:
            extracted_text_v3 = product_identifier_v3.group(0)

            if 'product' not in extracted_text_v3.lower() and\
                'supplier' not in extracted_text_v3.lower() and\
                'mixture' not in extracted_text_v3.lower() and\
                'section' not in extracted_text_v3.lower():

                if 'name' in extracted_text_v3.lower():
                    product_identifier_v4 = re_constructor(sequences["pi_v4"], extracted_text_v3)

                    if product_identifier_v4:
                        name = product_identifier_v4.group(0).split('\n')[-1].strip()
                        return name if len(name) > 3 else None
                else:
                    parts = extracted_text_v3.split('\n')
                    name = parts[1] + parts[2] if 'other' not in parts[2].lower() else parts[1]

                    return name if len(name) > 5 else None
    
        product_identifier_v5 = re_constructor(sequences["pi_v5"], page_text)

        if product_identifier_v5:
            extracted_text_v5 = product_identifier_v5.group(0)

            if '\n \n \n' not in extracted_text_v5:
                product_identifier_v6 = re_constructor(sequences["pi_v6"], extracted_text_v5)

                if product_identifier_v6:
                    extracted_text_v6 = product_identifier_v6.group(0).replace('\n', '').replace('\t', '').strip()
                    if 'product' not in extracted_text_v6.lower() and\
                        'application' not in extracted_text_v6.lower():
                        return extracted_text_v6


def other(page_text):
    """
        Some documents do not have certain order of text, 
            so it neccessary to find some of them manually.
    """
    other_v0 = re_constructor(sequences["oth_v0"], page_text)

    if other_v0:
        if len(other_v0.group(0)) > 1:
            extracted_text_v0 = other_v0.group(0).strip().split('\n')[1]
            return extracted_text_v0

    other_v1 = re_constructor(sequences["oth_v1"], page_text)

    if other_v1:
        extracted_text_v1 = other_v1.group(0).strip()
        other_v2 = re_constructor(sequences["oth_v2"], extracted_text_v1)

        if other_v2:
            extracted_text_v2 = other_v2.group(0).replace('\n', '').replace(':', '').strip()
            return extracted_text_v2

        other_v3 = re_constructor(sequences["oth_v3"], page_text)

        if other_v3:
            extracted_text_v3 = other_v3.group(0).strip().split('Trade name')

            if len(extracted_text_v3) > 1:
                name = extracted_text_v3[1].replace('\n', '').replace(':', '').strip()

                if 'product' not in name.lower() and\
                    'mixture' not in name.lower() and\
                        len(name) > 2:
                    return name



def company_name_finder(page_text):
    """
        The function tries to find the company name based on RegEX templates 
            from sequences dictionary
    """
    page_text = page_text.replace('\n \n \n', '\n')

    company_name_v0 = re_constructor(sequences["cn_v0"], page_text)

    if company_name_v0:
        extracted_text_v0 = company_name_v0.group(0).strip()
        name = extracted_text_v0.split(':')[1].strip()
        return name if len(name) > 2 else None

    company_name_v1 = re_constructor(sequences["cn_v1"], page_text)
    if company_name_v1:
        extracted_text_v1 = company_name_v1.group(0).strip().split('\n')

        if len(extracted_text_v1) > 1:
            name = extracted_text_v1[1].strip()
            return name if 'name' not in name.lower() else None

    company_name_v2 = re_constructor(sequences["cn_v2"], page_text, ignore_case=False)

    if company_name_v2:
        extracted_text_v2 = company_name_v2.group(0).strip().split('\n')
        if len(extracted_text_v2) > 1:
            name = extracted_text_v2[1].replace(':', '').strip()

            if len(name) > 1 and 'section' not in name.lower():
                return name


    company_name_v3 = re_constructor(sequences["cn_v3"], page_text)

    if company_name_v3:
        extracted_text_v3 = company_name_v3.group(0).strip().split('\n')

        if len(extracted_text_v3) > 1:
            return extracted_text_v3[1] if extracted_text_v3[1].strip().isalpha() else extracted_text_v3[-1]


    company_name_v4 = re_constructor(sequences["cn_v4"], page_text)

    if company_name_v4:
        extracted_text_v4 = company_name_v4.group(0).strip().split('\n')

        if len(extracted_text_v4) > 1:
            if 'address' not in extracted_text_v4[1].lower() and\
                'telephone' not in extracted_text_v4[1].lower() and\
                'name' not in extracted_text_v4[1].lower():
                return extracted_text_v4[1]

    company_name_v5 = re_constructor(sequences["cn_v5"], page_text, ignore_case=False)

    if company_name_v5:
        extracted_text_v5 = company_name_v5.group(0).strip().split('\n')

        if len(extracted_text_v5) > 1:
            if 'address' not in extracted_text_v5[1].lower() and\
                'telephone' not in extracted_text_v5[1].lower() and\
                'name' not in extracted_text_v5[1].lower():
                return extracted_text_v5[1]

    company_name_v6 = re_constructor(sequences["cn_v6"], page_text, ignore_case=False)

    if company_name_v6:
        extracted_text_v6 = company_name_v6.group(0).strip().split('data sheet')[-1].strip()
        return extracted_text_v6


def find_email(page_text):
    """
        The function tries to find the company email based on RegEX templates 
            from sequences dictionary
    """
    email_v0 = re_constructor(sequences["email_v0"], page_text)
    
    if email_v0:
        extracted_text_v0 = email_v0.group(0).strip()

        if ':' in extracted_text_v0:
            email = extracted_text_v0.split(':')[-1].strip()
            return email
        else:
            email = extracted_text_v0.strip()
            return email
    
    email_v1 = re_constructor(sequences["email_v1"], page_text)

    if email_v1:
        extracted_text_v1 = email_v1.group(0).strip()

        if ':' in extracted_text_v1:
            email = extracted_text_v1.split(':')[-1].strip()
            return email
        else:
            if '-' in extracted_text_v1:
                email = extracted_text_v1.split('-')
                return email[0].strip() if '@' in email[0] else email[-1].strip()

    email_v2 = re_constructor(sequences["email_v2"], page_text)

    if email_v2:
        return email_v2.group(0).strip()


def main(pdf, product_name=None, company_name=None):
    """
        The entry point of the script to execute all other function and check its outputs.
    """
    with fitz.Document(f'{PATH}/sds/{pdf}') as document:
        page = document.load_page(0)
        pg_text = page.get_text()

        pn = product_name_finder(pg_text)
        tn = trade_name_finder(pg_text)
        pi = product_identifier_finder(pg_text)
        oth = other(pg_text)


        if pn:
            product_name = pn
            company_name = company_name_finder(pg_text)

        elif tn:
            product_name = tn
            company_name = company_name_finder(pg_text)

        elif pi:
            product_name = pi
            company_name = company_name_finder(pg_text)

        elif oth:
            product_name = oth
            company_name = company_name_finder(pg_text)


        if not company_name:
            company_name_v0_1 = re_constructor(sequences["cn_v0_1"], pg_text)

            if company_name_v0_1:
                company_name = company_name_finder(pg_text[company_name_v0_1.span()[0]:])


    if product_name and company_name:
        product_name = product_name.replace('name:', '').replace('·', '')

        if len(product_name) < 3 or\
            len(company_name) <= 3 or\
                'Date' in product_name or\
                    '1.' in company_name or\
                        'name' in product_name.lower() or\
                            'name' in company_name.lower() or\
                                'number' in company_name.lower():
            return False

        email = find_email(pg_text)

        if email:
            return product_name.strip(), company_name.strip(), email


if __name__ == "__main__":
    PATH = str(pathlib.Path(__file__).parent)
    DIRECTORIES = os.listdir(PATH)
    PDF_LIST = None


    for directory in DIRECTORIES:
        if '.' not in directory:
            PDF_LIST = os.listdir(f'{PATH}/{directory}')
            break


    if PDF_LIST:
        with open(PATH + '/output.csv', 'w') as file:
            csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(('Product name', 'Company name', 'Email'))

            for pdf in PDF_LIST:
                success = main(pdf)

                if success:
                    csv_writer.writerow(success)
    else:
        print()
        print('-----The folder with PDFs is NOT FOUND!-----')
        print()