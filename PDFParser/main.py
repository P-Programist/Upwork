import os
import re
import fitz
import pathlib


PATH = str(pathlib.Path(__file__).parent)

pdf_list = os.listdir(f'{PATH}/sds')



# def product_identifier_finder(page_text):
#     template = r'\s?Product identifier.*\n.*\n.*'
#     product_identifier_re_v1 = re.compile(template, re.IGNORECASE)

#     product_identifier_v1 = re.search(product_identifier_re_v1, page_text)

#     if product_identifier_v1:
#         sep = product_identifier_v1.group(0).replace('\n', ' ')
        
#         p_ident = sep.lower().split('product identifier')[1]
#         if len(p_ident) < 7:    
#             template = r'Product identifier:.+\n.*\n.*\n.*\n'
#             product_identifier_re_v2 = re.compile(template, re.IGNORECASE)
#             product_identifier_v2 = re.search(product_identifier_re_v2, page_text)

#             if not product_identifier_v2:
#                 template = r'Name.+\n.*\n'
#                 product_identifier_re_v3 = re.compile(template, re.IGNORECASE)
#                 product_identifier_v3 = re.search(product_identifier_re_v3, page_text)
#                 if product_identifier_v3:
#                     sep2 = product_identifier_v3.group(0).replace('\n', ' ')
#                     return sep2
#             else:
#                 return sep
#         return sep
#     else:
#         template = r'Name.+\n.*\n.*\n'
#         product_identifier_re_v4 = re.compile(template, re.IGNORECASE)
#         product_identifier_v4 = re.search(product_identifier_re_v4, page_text)
#         if product_identifier_v4:
#             sep3 = product_identifier_v4.group(0).replace('\n', ' ')
#             return sep3


# def name_of_product_finder(page_text):
#     template = r'Product identifier.*\n.*\n'
#     product_identifier_re_v1 = re.compile(template, re.IGNORECASE)
#     product_identifier_v1 = re.search(product_identifier_re_v1, page_text)

#     if product_identifier_v1:
#         sep = product_identifier_v1.group(0).replace('\n', ' ')
#         if sep.count('Product') > 1:
#             template += r'.*\n.*'
#             product_identifier_re_v2 = re.compile(template, re.IGNORECASE)
#             product_identifier_v2 = re.search(product_identifier_re_v2, page_text)
#             sep2 = product_identifier_v2.group(0).replace('\n', ' ')
#             return sep2
#         return sep


# def indetification_of_substance_finder(page_text):
#     template=r'preparation.*\n.+\n.+\n.*'
#     indetification_of_substance_re_v1 = re.compile(template, re.IGNORECASE)
#     indetification_of_substance_v1 = re.search(indetification_of_substance_re_v1, page_text)

#     if indetification_of_substance_v1:
#         sep = indetification_of_substance_v1.group(0).replace('\n', ' ')
#         print(sep)


broken = (
    '100062.pdf',
    'High-Temp-MSDS-n7fy.pdf',
    'SDS_Insecticide_BL345-5.pdf',
    'WRX-Spray-Synthetic-Paint-MSDS.pdf',
    'Merged-COSHH-SDS-sheets.pdf',
    '019-msds-pink-wood-primer.pdf',
    'Flav-Blackberry-SDS.pdf',
    'MB50-001 20SDS 20(05-19).pdf'
)


def product_name_finder(page_text):
    template_v0 = r'Product name.*'
    product_name_re_v0 = re.compile(template_v0, re.IGNORECASE)
    product_name_v0 = re.search(product_name_re_v0, page_text)

    if product_name_v0:
        extracted_text_v0 = product_name_v0.group(0)

        template_v1 = r'name.+\w+.*'
        product_name_re_v1 = re.compile(template_v1, re.IGNORECASE)
        product_name_v1 = re.search(product_name_re_v1, extracted_text_v0)

        if product_name_v1:
            extracted_text_v1 = product_name_v1.group(0)

            template_v2 = r' :?.*'
            product_name_re_v2 = re.compile(template_v2, re.IGNORECASE)
            product_name_v2 = re.search(product_name_re_v2, extracted_text_v1)

            if product_name_v2:
                extracted_text_v2 = product_name_v2.group(0).replace(':', '').strip()

                return extracted_text_v2 if not extracted_text_v2.islower() else None


    template_v3 = r'Product name.*\n.*\n.*'
    product_name_re_v3 = re.compile(template_v3, re.IGNORECASE)
    product_name_v3 = re.search(product_name_re_v3, page_text)

    if product_name_v3:
        extracted_text_v3 = product_name_v3.group(0)

        template_v4 = r'\n.*\n'
        product_name_re_v4 = re.compile(template_v4, re.IGNORECASE)
        product_name_v4 = re.search(product_name_re_v4, extracted_text_v3)

        if product_name_v4:
            extracted_text_v4 = product_name_v4.group(0).strip('\n').strip()

            template_v5 = r'\w+.*'
            product_name_re_v5 = re.compile(template_v5, re.IGNORECASE)
            product_name_v5 = re.search(product_name_re_v5, extracted_text_v4)

            if product_name_v5:
                extracted_text_v5 = product_name_v5.group(0).strip()
                return extracted_text_v5 if 'date of issue' not in extracted_text_v5.lower() else None
            else:
                template_v6 = r'\n.*\n.*.?'
                product_name_re_v6 = re.compile(template_v6, re.IGNORECASE)
                product_name_v6 = re.search(product_name_re_v6, product_name_v3.group(0))

                if product_name_v6:
                    extracted_text_v6 = product_name_v6.group(0)

                    template_v7 = r'\w+.*'
                    product_name_re_v7 = re.compile(template_v7, re.IGNORECASE)
                    product_name_v7 = re.search(product_name_re_v7, extracted_text_v6)
                
                    if product_name_v7:
                        extracted_text_v7 = product_name_v7.group(0).strip()
                        if 'product' not in extracted_text_v7.lower()\
                            and 'substance' not in extracted_text_v7.lower()\
                                and 'trade' not in extracted_text_v7.lower():

                            return extracted_text_v7
    

def trade_name_finder(page_text):
    template_v0 = r'Trade name.*'
    trade_name_re_v0 = re.compile(template_v0, re.IGNORECASE)
    trade_name_v0 = re.search(trade_name_re_v0, page_text)

    if trade_name_v0:
        extracted_text_v0 = trade_name_v0.group(0)

        template_v1 = r'name:?.*'
        trade_name_re_v1 = re.compile(template_v1, re.IGNORECASE)
        trade_name_v1 = re.search(trade_name_re_v1, extracted_text_v0)

        if trade_name_v1:
            extracted_text_v1 = trade_name_v1.group(0)

            template_v2 = r' \w.*\W'
            trade_name_re_v2 = re.compile(template_v2, re.IGNORECASE)
            trade_name_v2 = re.search(trade_name_re_v2, extracted_text_v1)

            if trade_name_v2:
                extracted_text_v2 = trade_name_v2.group(0).strip()
                return extracted_text_v2 if not extracted_text_v2.islower() else None


def product_identifier_finder(page_text):
    template_v0 = r'Product identifier.*'
    product_identifier_re_v0 = re.compile(template_v0, re.IGNORECASE)
    product_identifier_v0 = re.search(product_identifier_re_v0, page_text)

    if product_identifier_v0:
        extracted_text_v0 = product_identifier_v0.group(0)

        template_v1 = r': \w.*'
        product_identifier_re_v1 = re.compile(template_v1, re.IGNORECASE)
        product_identifier_v1 = re.search(product_identifier_re_v1, extracted_text_v0)

        if product_identifier_v1:
            extracted_text_v1 = product_identifier_v1.group(0)
            return extracted_text_v1[2:]
        else:
            template_v2 = r'Product identifier.*\n.*\n.*\n'
            product_identifier_re_v2 = re.compile(template_v2, re.IGNORECASE)
            product_identifier_v2 = re.search(product_identifier_re_v2, page_text)

            if product_identifier_v2:
                extracted_text_v2 = product_identifier_v2.group(0)

                template_v3 = r'\n.*\n?\W?'
                product_identifier_re_v3 = re.compile(template_v3, re.IGNORECASE)
                product_identifier_v3 = re.search(product_identifier_re_v3, extracted_text_v2)

                # print(product_identifier_v3)
                if product_identifier_v3:
                    extracted_text_v3 = product_identifier_v3.group(0)

                    template_v4 = r'\w.*\w? ?'
                    product_identifier_re_v4 = re.compile(template_v4, re.IGNORECASE)
                    product_identifier_v4 = re.search(product_identifier_re_v4, extracted_text_v3)

                    if product_identifier_v4:
                        extracted_text_v4 = product_identifier_v4.group(0).strip()

                        if 'trade name' in extracted_text_v4.lower():
                            pass

                        elif 'product' in extracted_text_v4.lower():
                            pass
                        
                        print(extracted_text_v4)


for pdf in pdf_list:
    if pdf not in broken:
        with fitz.Document(f'{PATH}/sds/{pdf}') as document:
            page = document.load_page(0)
            pg_text = page.get_text()

            result_0 = product_name_finder(pg_text)

            if not result_0:
                result_1 = trade_name_finder(pg_text)
                if not result_1:
                    result_2 = product_identifier_finder(pg_text)

            #         if not result:
            #             result = indetification_of_substance_finder(pg_text)
            # if not result:
            #     print(pdf)
            #     print(repr(pg_text))
            #     print('-'*100)
 
            # if pdf == '1898_MSDS-Foam-P50.pdf':
            #     print(repr(pg_text))
        # print(pdf, sep)
