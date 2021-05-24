'''
Author: Azatot

The script automates the search of different Homes for sale of Redfin.com.
The script has 4 optional filters: City, Max-Price, Min-Price, Min-Bedrooms.

Please check whether You have Mozila Firefox or Google Chrome on your Computer.

The script depends on three major libraries: Selenium, BeautifulSoup, WebdriverManager.

The scenario of the script is the following:
    1. Ask a city from user.
    2. Ask other optional filters.
    3. Open automated browser and make a request with set filters.
    4. After a browser got a page of filtered results the script extracts all necessesary urls 
        to parse the rest of content recursively.
    5. As soon as the script found all links with potential data it makes request there and extract the data from HTML.
    6. After the data is extracted the script writes it into CSV file which calls data.csv and saves it next to itself.


The price for Zip Code and Total # of Bedrooms is based on relations.py file which was generated according to provided price list.
'''
import os
import time
import asyncio
import aiohttp
import pathlib
import aiofiles


import numpy_financial as npf
from aiocsv import AsyncWriter
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


from relations import prices



HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Content-Type": "text/plain;charset=UTF-8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}


PATH = pathlib.Path(__file__).parent


class Authorization(object):

    def __init__(self, url):
        super(Authorization, self).__init__()
        self.url = url
        self.url_split = url

        self.options = Options()
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        self.options.add_argument("start-fullscreen")

    def start_browser(self) -> str:
        chromedriver_path = str(PATH) + '/chromedriver_linux64/chromedriver'

        try:
            self.browser = webdriver.Chrome(options=self.options, executable_path=chromedriver_path)
            time.sleep(3)
            self.browser.get(self.url)
            return 1
        except:
            try:
                self.chrome_service = Service(ChromeDriverManager().install())
                self.browser = webdriver.Chrome(options=self.options, service=self.chrome_service)
                time.sleep(3)
                self.browser.get(self.url)
                return 1
            except:
                try:
                    self.chrome_service = Service(chromedriver_path)
                    self.browser = webdriver.Chrome(options=self.options, service=self.chrome_service)
                    time.sleep(3)
                    self.browser.get(self.url)
                    return 1
                except:
                    return 0



    def get_filtered_pages(self, filters):
        search_from = self.browser.find_element(By.ID, "search-box-input")

        search_button = self.browser.find_element(By.CLASS_NAME, "inline-block.SearchButton.clickable.float-right")

        search_from.click()
        time.sleep(1)

        search_from.send_keys(filters.get('city'))
        time.sleep(1)

        search_button.click()
        time.sleep(4)

        url = self.browser.current_url + '/filter/property-type=multifamily'

        if filters.get('max-price'):
            max_price = filters.get('max-price')
            url += f',max-price={max_price}'

        if filters.get('min-beds'):
            min_beds = filters.get('min-beds')
            url += f',min-beds={min_beds}'

        if filters.get('min-price'):
            min_price = filters.get('min-price')
            url += f',min-price={min_price}'

        self.browser.get(url)

        try:
            pagination = self.browser.find_element(By.CLASS_NAME, "PagingControls")
            pagination_links = pagination.find_elements(By.TAG_NAME, "a")

            return (link.get_attribute("href") for link in pagination_links)
        except:
            return (url,)


    def quit_bowser(self):
        return self.browser.quit()


class DataMiner:
    async def get_data(self, url):
        await asyncio.sleep(2.5)
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            try:
                request = await session.get(url)
                html = await request.text()
                return html
            except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError):
                return []


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
            interior = soup.find('div', class_='propertyDetailContainer-content useColumnCount')

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
                            temp_view_data.append(prices.get(zip_code).get(int(total_bedrooms)))


                if 'Unit #' in frame_header.text:
                    unit_info = frame.ul.find_all('li')

                    for unit in unit_info:
                        if 'Bedroom' in unit.text:
                            bedrooms_per_unit = unit.text.split()[-1]
                            temp_view_data.append(bedrooms_per_unit)
                            temp_view_data.append(prices.get(zip_code).get(int(bedrooms_per_unit)))

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



def set_filters():
    FILTER_FIELDS = {}

    CITY = input('What CITY You are looking for (Leave empty and Press Enter -> to skip): ')
    MIN_PRICE = input('What MINIMAL PRICE You are looking for (Leave empty and Press Enter -> to skip): ')
    MAX_PRICE = input('What MAXIMUM PRICE You are looking for (Leave empty and Press Enter -> to skip): ')
    MIN_BEDS = input('What MINIMUM BEDS You are looking for (Leave empty and Press Enter -> to skip): ')


    if CITY:
        FILTER_FIELDS["city"] = CITY

    if MIN_PRICE:
        FILTER_FIELDS["min-price"] = MIN_PRICE

    if MAX_PRICE:
        FILTER_FIELDS["max-price"] = MAX_PRICE

    if MIN_BEDS:
        FILTER_FIELDS["min-beds"] = MIN_BEDS

    return FILTER_FIELDS


def net_cashflow_calculator(data):
    result = {}

    interest_rate = 0.0425 # C5
    tax_rate = 0.01 # E2
    duration_of_loan_in_months = 360 # C6
    monthly_property_insurance = 150 # E5
    down_payment_percent = 0.2 # E7
    property_managment = 0.05 # E8
    total_price = data.get('total_price') # C4


    unit_prices = []

    if data.get('unit_1'):
        unit_prices.append(data.get('unit_1'))

    if data.get('unit_2'):
        unit_prices.append(data.get('unit_2'))

    if data.get('unit_3'):
        unit_prices.append(data.get('unit_3'))

    if data.get('unit_4'):
        unit_prices.append(data.get('unit_4'))


    loan_amount = round((1-down_payment_percent) * total_price, 2) # C7
    down_payment_summ = round(down_payment_percent * total_price, 2) # C8
    principal_and_interest = round(npf.pmt(interest_rate/12, duration_of_loan_in_months, -loan_amount, 2), 1) # E4
    monthly_property_tax_amount = round(total_price * tax_rate / 12, 2) # E6
    pmt_summ = round((loan_amount * interest_rate) / 12, 7) # E10
    gross_rent_monthly = sum(unit_prices) # C11
    property_management_summ = property_managment * gross_rent_monthly # C19
    interest_only_loan_summ = sum(unit_prices[:3]) - property_management_summ - monthly_property_tax_amount - monthly_property_insurance - pmt_summ # C9
    gross_rent_annual = gross_rent_monthly * 12 # D11
    monthly_net_cashflow = round(gross_rent_monthly - property_management_summ - principal_and_interest - monthly_property_insurance - monthly_property_tax_amount, 2)# C20
    annual_net_cashflow = round(monthly_net_cashflow * 12, 2) # C21
    interest_only_loan_percent = round((interest_only_loan_summ * 12) / down_payment_summ, 2)
    total_invested = int(down_payment_summ + 0) # E 20
    pay_off_in_years = round(down_payment_summ / annual_net_cashflow, 2) # E 21
    return_on_investment = round(annual_net_cashflow / total_invested, 2) * 100 # E 13
    monthly_loan_payment = monthly_property_insurance + principal_and_interest + monthly_property_tax_amount # D 2


    result["loan_amount"] = loan_amount
    result["down_payment_summ"] = down_payment_summ
    result["principal_and_interest"] = principal_and_interest
    result["monthly_property_tax_amount"] = monthly_property_tax_amount
    result["interest_only_loan_summ"] = interest_only_loan_summ
    result["interest_only_loan_percent"] = interest_only_loan_percent
    result["pmt_summ"] = pmt_summ
    result["gross_rent_monthly"] = gross_rent_monthly
    result["gross_rent_annual"] = gross_rent_annual
    result["property_management_summ"] = property_management_summ
    result["monthly_net_cashflow"] = monthly_net_cashflow
    result["annual_net_cashflow"] = annual_net_cashflow
    result["total_invested"] = total_invested
    result["return_on_investment"] = return_on_investment
    result["monthly_loan_payment"] = monthly_loan_payment

    return result


async def main():
    FILTER_FIELDS = set_filters()

    auth = Authorization('https://www.redfin.com')
    browser = auth.start_browser()

    if not browser:
        print('---------------Browser is not found or ChromeDriver is not installed!---------------')
        return auth.quit_bowser()

    try:
        pages = auth.get_filtered_pages(FILTER_FIELDS)
    except:
        print('--------- Check internet connection and try again! ---------')
        return auth.quit_bowser()


    dtmnr = DataMiner()

    page_views = await asyncio.gather(*(dtmnr.get_data(page) for page in pages))
    pagination_urls = (dtmnr.get_each_property_url(page_view) for page_view in page_views)

    auth.quit_bowser()

    async with aiofiles.open(
        file=str(PATH) + "/data.csv", mode="w", 
        encoding="utf-8", newline="") as afp:
        
        writer = AsyncWriter(afp, dialect="unix")
        await writer.writerow(["PropertyAddress", "ZipCode", "TotalPrice", "UnitsTotal", "BedroomsTotal", "PriceForTotalBedrooms", "Unit1", "PriceForUnit1",  "Unit2", "PriceForUnit2",  "Unit3", "PriceForUnit3",  "Unit4", "PriceForUnit4", "MonthlyNetCashflow", "AnnualNetCashflow", "ReturnOnInvestment"])

        for pagination_url in pagination_urls:
            await asyncio.sleep(1.4)
            rows = await asyncio.gather(*(dtmnr.get_property_info(url) for url in tuple(url for url in pagination_url)))
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



if __name__ == "__main__":
    asyncio.run(main())
