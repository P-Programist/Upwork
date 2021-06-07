'''
Author: Azatot

The script automates the search of different Homes for sale of Redfin.com.
The script has 4 optional filters: City, Max-Price, Min-Price, Min-Bedrooms.

Please check whether You have Mozila Firefox or Google Chrome on your Computer.

The script depends on three major libraries: Selenium, BeautifulSoup, WebdriverManager.

The scenario of the script is the following:
    1. Ask a link from a user.
    2. The next step is to make request according to the set filters and get all pagination urls as well.
    3. As soon as the script found all links with potential data it makes request there and extract the data from HTML.
    4. After the data is extracted the script writes it into CSV file which calls data.csv and saves it next to itself.


# of Bedrooms is based on relations.py file which was generated according to provided price list.
The price for Zip Code and Total
'''

import asyncio
import aiohttp
import pathlib
import aiofiles


import numpy_financial as npf
from aiocsv import AsyncWriter
from bs4 import BeautifulSoup as bs

from relations import prices


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://www.redfin.com/",
    "Upgrade-Insecure-Requests": "1",
    "Content-Type": "text/plain;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Cookie": '''RF_CORVAIR_LAST_VERSION=368.0.0; RF_BROWSER_ID=uJN8rqjGRtqmOEz08L2_Qg; RF_BID_UPDATED=1; sortOrder=1; sortOption=special_blend; AKA_A2=A; AMP_TOKEN=%24NOT_FOUND; FEED_COUNT=0%3At; _uetsid=102ac700bdd911eb9e48ad579aa122bb; _uetvid=a21dd430b60411eba172e70ab6a3901d; _dc_gtm_UA-294985-1=1; audS=t'''
}


PATH = pathlib.Path(__file__).parent


class DataMiner:
    def __init__(self, url) -> None:
        self.url = url
        

    async def get_data(self, url):
        await asyncio.sleep(2)
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            try:
                request = await session.get(url)
                html = await request.text()
                if 'Oops!  It looks like' in html:
                    print('----- Your IP has been blocked! -----')
                    return []
                else:
                    return html
            except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
                print('----- Inernet connection has been lost! -----')
                return []


    async def get_pages(self):
        html = await self.get_data(self.url)

        if html:
            soup = bs(html, 'html.parser')
            pagination_buttons = soup.find('div', class_='PagingControls')

            if pagination_buttons:
                links = ['https://www.redfin.com'+link["href"] for link in pagination_buttons.find_all('a')]
                return links
            else:
                return (self.url,)


    def get_each_property_url(self, html):
        soup = bs(html, 'html.parser')
        home_views = soup.find_all('div', class_='HomeViews')

        for view in home_views:
            all_offers = view.find_all('div', class_="HomeCardContainer")
            for offer in all_offers:
                if offer.a:
                    href = offer.a["href"]
                    yield 'https://www.redfin.com' + href



    async def get_property_info(self, url):
        data = await self.get_data(url)

        if data:
            temp_view_data = []

            soup = bs(data, 'html.parser')
            interior = soup.find(
                'div', class_='propertyDetailContainer-content useColumnCount')

            if not interior:
                return [0 for _ in range(13)]

            frames = interior.find_all('div', class_='propertyDetailItem')

            address = soup.find('div', class_='street-address')
            zip_code = soup.find('div', class_='dp-subtext')
            price = soup.find('div', class_='statsValue')

            if address:
                temp_view_data.append(address.text)

            if zip_code:
                zip_code = zip_code.text.split()[-1]

            if price:
                price = int(price.text.split('$')[-1].replace(',', ''))

            temp_view_data.append(zip_code)
            temp_view_data.append(price)

            for frame in frames:
                frame_header = frame.find('div', class_='listHeader')

                if frame_header.text == 'Multi-Family Information':
                    totals = frame.ul.find_all('li')
                    units_number = int(totals[0].span.text.split()[-1])

                    temp_view_data.append(units_number)

                    for total in totals:
                        if 'Bedrooms' in total.span.text:
                            total_bedrooms = total.span.text.split()[-1]
                            temp_view_data.append(total_bedrooms)
                            temp_view_data.append(prices.get(
                                zip_code).get(int(total_bedrooms)))

                if 'Unit #' in frame_header.text:
                    unit_info = frame.ul.find_all('li')

                    for unit in unit_info:
                        if 'Bedroom' in unit.text:
                            bedrooms_per_unit = unit.text.split()[-1]
                            temp_view_data.append(bedrooms_per_unit)
                            temp_view_data.append(prices.get(
                                zip_code).get(int(bedrooms_per_unit)))

            for _ in range(14 - len(temp_view_data)):
                temp_view_data.append(0)

            temp_view_data_updated = []

            for i in temp_view_data:
                if i:
                    temp_view_data_updated.append(i)
                else:
                    temp_view_data_updated.append(0)

            if temp_view_data_updated and len(temp_view_data_updated) > 1:
                return temp_view_data_updated

        return [0 for _ in range(15)]



def net_cashflow_calculator(data):
    result = {}

    interest_rate = 0.0425  # C5
    tax_rate = 0.01  # E2
    duration_of_loan_in_months = 360  # C6
    monthly_property_insurance = 150  # E5
    down_payment_percent = 0.2  # E7
    property_managment = 0.05  # E8
    total_price = data.get('total_price')  # C4

    unit_prices = []

    if data.get('unit_1'):
        unit_prices.append(data.get('unit_1'))

    if data.get('unit_2'):
        unit_prices.append(data.get('unit_2'))

    if data.get('unit_3'):
        unit_prices.append(data.get('unit_3'))

    if data.get('unit_4'):
        unit_prices.append(data.get('unit_4'))

    loan_amount = round((1-down_payment_percent) * total_price, 2)  # C7
    down_payment_summ = round(down_payment_percent * total_price, 2)  # C8
    principal_and_interest = round(
        npf.pmt(interest_rate/12, duration_of_loan_in_months, -loan_amount, 2), 1)  # E4
    monthly_property_tax_amount = round(total_price * tax_rate / 12, 2)  # E6
    # pmt_summ = round((loan_amount * interest_rate) / 12, 7) # E10
    gross_rent_monthly = sum(unit_prices)  # C11
    property_management_summ = property_managment * gross_rent_monthly  # C19
    # interest_only_loan_summ = sum(unit_prices[:3]) - property_management_summ - monthly_property_tax_amount - monthly_property_insurance - pmt_summ # C9
    # gross_rent_annual = gross_rent_monthly * 12 # D11
    monthly_net_cashflow = round(gross_rent_monthly - property_management_summ -
                                 principal_and_interest - monthly_property_insurance - monthly_property_tax_amount, 2)  # C20
    annual_net_cashflow = round(monthly_net_cashflow * 12, 2)  # C21
    # interest_only_loan_percent = round((interest_only_loan_summ * 12) / down_payment_summ, 2)
    total_invested = int(down_payment_summ + 0)  # E 20
    # pay_off_in_years = round(down_payment_summ / annual_net_cashflow, 2) # E 21
    
    if total_invested:
        return_on_investment = int(
            round(annual_net_cashflow / total_invested, 2) * 100)  # E 13
    else:
        return_on_investment = 0
        

    # monthly_loan_payment = monthly_property_insurance + principal_and_interest + monthly_property_tax_amount # D 2

    # result["loan_amount"] = loan_amount
    # result["down_payment_summ"] = down_payment_summ
    # result["principal_and_interest"] = principal_and_interest
    # result["monthly_property_tax_amount"] = monthly_property_tax_amount
    # result["interest_only_loan_summ"] = interest_only_loan_summ
    # result["interest_only_loan_percent"] = interest_only_loan_percent
    # result["pmt_summ"] = pmt_summ
    # result["gross_rent_monthly"] = gross_rent_monthly
    # result["gross_rent_annual"] = gross_rent_annual
    # result["property_management_summ"] = property_management_summ
    result["monthly_net_cashflow"] = monthly_net_cashflow
    result["annual_net_cashflow"] = annual_net_cashflow
    # result["total_invested"] = total_invested
    result["return_on_investment"] = return_on_investment
    # result["monthly_loan_payment"] = monthly_loan_payment

    return result


async def main(url):
    dtmnr = DataMiner(url)
    pages = await dtmnr.get_pages()

    if pages:
        page_views = await asyncio.gather(*(dtmnr.get_data(page) for page in pages))
        pagination_urls = (dtmnr.get_each_property_url(page_view) for page_view in page_views)


        async with aiofiles.open(
                file=str(PATH) + "/data.csv", mode="w",
                encoding="utf-8", newline="") as afp:

            writer = AsyncWriter(afp, dialect="unix")
            await writer.writerow(["PropertyAddress", "ZipCode", "TotalPrice", "UnitsTotal", "BedroomsTotal", "PriceForTotalBedrooms", "Unit1", "PriceForUnit1",  "Unit2", "PriceForUnit2",  "Unit3", "PriceForUnit3",  "Unit4", "PriceForUnit4", "MonthlyNetCashflow", "AnnualNetCashflow", "ReturnOnInvestment"])

            for pagination_url in pagination_urls:
                print('----- Please Wait... The program collects the data! -----')
                await asyncio.sleep(1.8)
                rows = await asyncio.gather(*(dtmnr.get_property_info(url) for url in tuple(url for url in pagination_url)))

                if rows:
                    for row in rows:
                        array = {
                            "total_price": row[2]
                        }

                        array["unit_1"] = row[7]
                        array["unit_2"] = row[9]
                        array["unit_3"] = row[11]
                        array["unit_4"] = row[13]

                        calculations = net_cashflow_calculator(array)
                        row.append(calculations.get("monthly_net_cashflow"))
                        row.append(calculations.get("annual_net_cashflow"))
                        row.append(calculations.get("return_on_investment"))
                        await writer.writerow(row)
                else:
                    print('----- There is no information with these filters! -----')
                    return 0
        return 1


if __name__ == "__main__":
    url = input('Please insert URL: ')
    if asyncio.run(main(url)):
        print('----- Success, Check data.csv file!')
