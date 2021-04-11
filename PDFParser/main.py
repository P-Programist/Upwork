import os
import re
import fitz
import pathlib

PATH = str(pathlib.Path(__file__).parent)

pdf_list = os.listdir(f'{PATH}/sds')


broken = (
    '100062.pdf',
    'High-Temp-MSDS-n7fy.pdf',
    'SDS_Insecticide_BL345-5.pdf',
    'WRX-Spray-Synthetic-Paint-MSDS.pdf',
    'Merged-COSHH-SDS-sheets.pdf',
    '019-msds-pink-wood-primer.pdf',
    'Flav-Blackberry-SDS.pdf',
    'MB50-001 20SDS 20(05-19).pdf',
    'ec-9323-msds-new.pdf',
    'Clean-Cotton-SDS-for-100-oil.pdf',
    'SDS-UK-EU-English-ACQ-1900-8020521.pdf',
    '72504-GB-SDS-Foamy-Lube-Spray.pdf',
    'Flexyfix-SDS-Rev-301.pdf',
    'MAXBIT-SKW-SDS.pdf',
    'Crown-Contract-QD-Satin-CLP-SDS-100217.pdf',
    'Sadolin-PV-67-Varnish-SDS-2015.pdf',
    'SDS_C51_E_11_10.pdf',
    'EcosystemNaturalDiffuserBaseSDS.pdf',
    'chess_wg_sds_141217.pdf',
    'Dimethoate_40_MSDS.pdf',
    'EN 20- 20MS 20Rodetox 20DIF 20Wheat_merged.pdf',
    'DS701-Dentigel-75-SDS-010620.pdf',
    'hd141_MSDS.pdf',
    'Ican-Luxeduck-MSDS-1.pdf',
    'Calendula-SDS.pdf',
    'Moyne-Roberts-1-AFFF_MSDS.pdf',
    'Ref-6-SDS-Endosan-5.pdf',
    'Black_Resin_-_SDS_EU_.pdf',
    'SDS-02.01-Cement-Based-Products-V10-August-2016.pdf',
    'Anti-Bug_Kill_SDS_v2.0.pdf',
    'escentscia-4dance.pdf',
    'Mixture-B-Safety-Data-Sheet.pdf',
    '3M 203779 20MSDS.Image.Marked.pdf',
    'HEAVY-DUTY-SEALER-MSDS-24.pdf',
    'mupdf: expected object number',
    '56PAINT400SG.pdf',
    'Eico-Alterior-Gloss-MSDS.pdf',
    'CRG747 20Rinse 20Aid 205ltr 20- 20MAR 2016.pdf',
    'MUEX6-MultiChem-2-MSDS.pdf',
    '385 203M 20Photo 20Mount 20Aerosol 20Adhesive 20400ml 20MSDS.pdf',
    'WG-PRIME-Atomizer 20White 20Grease 20CLP 20SDS.pdf',
    'Macpherson-Acrylic-Primer-Undercoat-CLP-SDS-090617.pdf',
    'YTA910_MSDS.pdf',
    'CamcleanMSDS.pdf',
    'AG090-3_MSDS.pdf',
    'Candle-SDS-Dark-Honey-Tobacco-10.pdf',
    'Iron-iii-Oxide-Synthetic-SDS.pdf',

)


def re_constructor(sequence, text):
    template = re.compile(sequence, re.IGNORECASE)
    result = re.search(template, text)

    return result

    


def product_name_finder(page_text):
    sequences = {
        "pn_v0": r"Product name.*",

    }

    product_name_v0 = re_constructor(sequences["pn_v0"], page_text)

    # template_v0 = r'Product name.*'
    # product_name_re_v0 = re.compile(template_v0, re.IGNORECASE)
    # product_name_v0 = re.search(product_name_re_v0, page_text)

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
    template_v0 = r'e name.?\n.+\n.*'
    trade_name_re_v0 = re.compile(template_v0, re.IGNORECASE)
    trade_name_v0 = re.search(trade_name_re_v0, page_text)

    if trade_name_v0:
        extracted_text_v0 = trade_name_v0.group(0)
 
        template_v2 = r': \n?\w.*\W'
        trade_name_re_v2 = re.compile(template_v2, re.IGNORECASE)
        trade_name_v2 = re.search(trade_name_re_v2, extracted_text_v0)

        if trade_name_v2:
            extracted_text_v2 = trade_name_v2.group(0).replace('\n', '').replace(':', '').strip()
            return extracted_text_v2

    else:
        template_v3 = r'Trade name ?:.+\n?.*\n'
        trade_name_re_v3 = re.compile(template_v3, re.IGNORECASE)
        trade_name_v3 = re.search(trade_name_re_v3, page_text)

        if trade_name_v3:
            extracted_text_v3 = trade_name_v3.group(0).strip()

            template_v4 = r':.*\n?'
            trade_name_re_v4 = re.compile(template_v4, re.IGNORECASE)
            trade_name_v4 = re.search(trade_name_re_v4, extracted_text_v3)

            if trade_name_v4:
                extracted_text_v4 = trade_name_v4.group(0).replace(': ', '').strip()
                return extracted_text_v4 if len(extracted_text_v4) > 3 else None


def product_identifier_finder(page_text):
    template_v0 = r'Product identifier? \n?.*\n?'
    product_identifier_re_v0 = re.compile(template_v0, re.IGNORECASE)
    product_identifier_v0 = re.search(product_identifier_re_v0, page_text)

    if product_identifier_v0:
        extracted_text_v0 = product_identifier_v0.group(0)

        template_v1 = r'\n.*\n'
        product_identifier_re_v1 = re.compile(template_v1, re.IGNORECASE)
        product_identifier_v1 = re.search(product_identifier_re_v1, extracted_text_v0)

        if product_identifier_v1:
            extracted_text_v1 = product_identifier_v1.group(0)
            if 'Product' not in extracted_text_v1 and\
                    'name' not in extracted_text_v1.lower() and\
                        len(extracted_text_v1) > 3 and\
                            'mixture' not in extracted_text_v1.lower():

                return extracted_text_v1.replace('\n', '').strip()
    else:
        template_v2 = r'Product identifier.*\n?.*\n?.*\n?.*'
        product_identifier_re_v2 = re.compile(template_v2, re.IGNORECASE)
        product_identifier_v2 = re.search(product_identifier_re_v2, page_text)

        if product_identifier_v2:
            extracted_text_v2 = product_identifier_v2.group(0)

            template_v3 = '\n.*\n.*\n'
            product_identifier_re_v3 = re.compile(template_v3, re.IGNORECASE)
            product_identifier_v3 = re.search(product_identifier_re_v3, extracted_text_v2)

            if product_identifier_v3:
                extracted_text_v3 = product_identifier_v3.group(0)

                if 'product' not in extracted_text_v3.lower() and\
                    'supplier' not in extracted_text_v3.lower() and\
                    'mixture' not in extracted_text_v3.lower() and\
                    'section' not in extracted_text_v3.lower():

                    if 'name' in extracted_text_v3.lower():
                        template_v4 = 'name:?\n?.*'
                        product_identifier_re_v4 = re.compile(template_v4, re.IGNORECASE)
                        product_identifier_v4 = re.search(product_identifier_re_v4, extracted_text_v3)

                        if product_identifier_v4:
                            name = product_identifier_v4.group(0).split('\n')[-1].strip()
                            return name if len(name) > 3 else None

                    else:
                        parts = extracted_text_v3.split('\n')
                        name = parts[1] + parts[2] if 'other' not in parts[2].lower() else parts[1]

                        return name if len(name) > 5 else None
        else:
            template_v4 = 'name.?\n?.*\n?.*\n?.*\n'
            product_identifier_re_v4 = re.compile(template_v4, re.IGNORECASE)
            product_identifier_v4 = re.search(product_identifier_re_v4, page_text)

            if product_identifier_v4:
                extracted_text_v4 = product_identifier_v4.group(0)

                if '\n \n \n' not in extracted_text_v4:
                    template_v5 = '\n\w+.*'
                    product_identifier_re_v5 = re.compile(template_v5, re.IGNORECASE)
                    product_identifier_v5 = re.search(product_identifier_re_v5, extracted_text_v4)

                    if product_identifier_v5:
                        extracted_text_v5 = product_identifier_v5.group(0).replace('\n', '').replace('\t', '').strip()

                        if 'product' not in extracted_text_v5.lower() and\
                            'application' not in extracted_text_v5.lower():
                            return extracted_text_v5


def other(page_text):
    template_v0 = 'Name of product.?\n?\w.*\n'
    other_re_v0 = re.compile(template_v0, re.IGNORECASE)
    other_v0 = re.search(other_re_v0, page_text)

    if other_v0:
        if len(other_v0.group(0)) > 1:
            extracted_text_v0 = other_v0.group(0).strip().split('\n')[1]
            return extracted_text_v0

    else:
        template_v1 = r'\nProduct identifier:?.?\n.*\n.*'
        other_re_v1 = re.compile(template_v1, re.IGNORECASE)
        other_v1 = re.search(other_re_v1, page_text)

        if other_v1:
            extracted_text_v1 = other_v1.group(0).strip()

            template_v2 = r': \n?.*\n.*'
            other_re_v2 = re.compile(template_v2, re.IGNORECASE)
            other_v2 = re.search(other_re_v2, extracted_text_v1)

            if other_v2:
                extracted_text_v2 = other_v2.group(0).replace('\n', '').replace(':', '').strip()
                return extracted_text_v2
        else:
            template_v3 = r'Trade name.*\n.*\n'
            other_re_v3 = re.compile(template_v3)
            other_v3 = re.search(other_re_v3, page_text)

            if other_v3:
                extracted_text_v3 = other_v3.group(0).strip().split('Trade name')[1]
                name = extracted_text_v3.replace('\n', '').replace(':', '').strip()
                if 'product' not in name.lower() and\
                    'mixture' not in name.lower() and\
                        len(name) > 2:
                    return name

            

n = 0
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

                    if not result_2:
                        result_3 = other(pg_text)

                        if result_3:
                            n += 1
                            # print(result_3)
                    else:
                        n += 1
                        # print(result_2)
                else:
                    n += 1
                    # print(result_1)
            else:
                n += 1
                # print(result_0)


print(n/len(pdf_list)*100)
