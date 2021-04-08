import os
import re
import fitz
import pathlib


PATH = str(pathlib.Path(__file__).parent)

pdf_list = os.listdir(f'{PATH}/sds')

def product_name_finder(page_text):
    product_name_re_v1 = re.compile(r'Product name.*\n.*', re.IGNORECASE)
    product_name_re_v2 = re.compile(r'Product name.\n: \n.*\n', re.IGNORECASE)

    product_name_v1 = re.search(product_name_re_v1, page_text)

    if product_name_v1:
        sep = product_name_v1.group(0).replace('\n', ' ')

        if len(sep) <= 16:
            product_name_v2 = re.search(product_name_re_v2, page_text)
            if product_name_v2:
                sep = product_name_v2.group(0).replace('\n', ' ')
                return sep
            else:
                return False
        else:
           return sep

    return False
    

def trade_name_finder(page_text):
    template = r'Trade name.*\n.*\n'
    trade_name_re_v1 = re.compile(template, re.IGNORECASE)

    trade_name_v1 = re.search(trade_name_re_v1, page_text)
    

    if trade_name_v1:
        sep2 = trade_name_v1.group(0).replace('\n', ' ')
       
        if len(sep2) <= 15:
            template += '.*\n'

            trade_name_re_v2 = re.compile(template, re.IGNORECASE)
            trade_name_v2 = re.search(trade_name_re_v2, page_text)

            if trade_name_v2:
                sep3 = trade_name_v2.group(0).replace('\n', ' ')
                if len(sep3) <= 16:
                    template += '.*\n'
                    product_name_v3 = re.search(template, page_text)
                    if product_name_v3:
                        sep4 = product_name_v3.group(0).replace('\n', ' ')
                        return sep4
                    else:
                        return False
                return sep3
        else:
            return sep2

    return False


def product_identifier_finder(page_text):
    template = r'Product identifier.*\n.*\n'
    product_identifier_re_v1 = re.compile(template, re.IGNORECASE)

    product_identifier_v1 = re.search(product_identifier_re_v1, page_text)

    if product_identifier_v1:
        sep = product_identifier_v1.group(0).replace('\n', ' ')
        # print(repr(page_text))
        print('--'*70)
        return sep


def name_of_product_finder(page_text):
    template = r'Product identifier.*\n.*\n'
    product_identifier_re_v1 = re.compile(template, re.IGNORECASE)
    product_identifier_v1 = re.search(product_identifier_re_v1, page_text)

    if product_identifier_v1:
        sep = product_identifier_v1.group(0).replace('\n', ' ')
        if sep.count('Product') > 1:
            template += r'.*\n.*'
            product_identifier_re_v2 = re.compile(template, re.IGNORECASE)
            product_identifier_v2 = re.search(product_identifier_re_v2, page_text)
            sep2 = product_identifier_v2.group(0).replace('\n', ' ')
            print(sep2)
        print('--'*70)
        return sep

broken = (
    '100062.pdf',
    'High-Temp-MSDS-n7fy.pdf',
    'SDS_Insecticide_BL345-5.pdf',
    'WRX-Spray-Synthetic-Paint-MSDS.pdf'
)

for pdf in pdf_list[:50]:
    if pdf not in broken:
        with fitz.Document(f'{PATH}/sds/{pdf}') as document:
            page = document.load_page(0)
            pg_text = page.get_text()
            sep = product_name_finder(pg_text)
            if not sep:
                sep2 = trade_name_finder(pg_text)
                if not sep2:
                    print(pdf, product_identifier_finder(pg_text))
 
            # if pdf == 'Clean-Cotton-SDS-for-100-oil.pdf':
            #     print(repr(pg_text))
        # print(pdf, sep)

        # print('-'*100)
        # if product_name_finder(pg_text) == 2:
        #     page = document.load_page(1)
        #     pg_text = page.get_text()



# print(errors/len(pdf_list) * 100)
# with fitz.Document(f'/home/azatot/Desktop/Computer_Science/P-Programist/Projects/Commercial/Upwork/PDFParser/sds/003.004S-Allied_Hygiene_Safehands_Hand_Sanitising_Wipes_MSDS.pdf') as document:
#     page = document.load_page(0)
#     areas = page.get_text()

#     product_name_re_v1 = re.compile(r'Product name', re.IGNORECASE)
#     product_name_re_v2 = re.compile(r'Product name', re.IGNORECASE)

#     r1 = re.search(product_name_re_v1, areas)
#     r2 = re.search(product_name_re_v2, areas)


