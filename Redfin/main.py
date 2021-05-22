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


import sys
import time
import asyncio
import aiohttp
import pathlib
import aiofiles

from aiocsv import AsyncWriter
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

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

        self.options = Options()
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")


    def start_browser(self) -> str:
        if sys.platform == 'win32':
            self.chrome_service = Service(ChromeDriverManager().install())
            self.options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            self.browser = webdriver.Chrome(options=self.options, service=self.chrome_service)

            try:
                self.browser = webdriver.Chrome(options=self.options, service=self.chrome_service)
            except exceptions.WebDriverException:
                self.firefox_service = Service(GeckoDriverManager().install())
                self.browser = webdriver.Firefox(service=self.firefox_service)
        else:
            self.firefox_service = Service(GeckoDriverManager().install())
            self.browser = webdriver.Firefox(service=self.firefox_service)

        self.browser.maximize_window()

        return self.browser.get(self.url)


    def get_filtered_pages(self, filters):
        search_from = self.browser.find_element(By.ID, "search-box-input")

        search_button = self.browser.find_element(By.CLASS_NAME, "inline-block.SearchButton.clickable.float-right")

        search_from.click()
        time.sleep(0.5)

        search_from.send_keys(filters.get('city'))
        time.sleep(0.5)

        search_button.click()
        time.sleep(2)

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

        pagination = self.browser.find_element(By.CLASS_NAME, "PagingControls")
        pagination_links = pagination.find_elements(By.TAG_NAME, "a")

        return (link.get_attribute("href") for link in pagination_links)


    def quit_bowser(self):
        return self.browser.quit()



class DataMiner:
    async def get_data(self, url):
        await asyncio.sleep(1.5)
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
                return ["" for _ in range(13)]

            frames = interior.find_all('div', class_='propertyDetailItem')

            address = soup.find('div', class_='street-address')
            zip_code = soup.find('div', class_='dp-subtext')

            if address:
                temp_view_data.append(address.text)

            if zip_code:
                zip_code = zip_code.text.split()[-1]
            
            temp_view_data.append(zip_code)

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


            temp_view_data_updated = []

            for i in temp_view_data:
                if i:
                    temp_view_data_updated.append(i)
                else:
                        temp_view_data_updated.append(0)

            if temp_view_data_updated and len(temp_view_data_updated) > 1:
               return temp_view_data_updated

        return ["" for _ in range(13)] 




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



async def main():
    FILTER_FIELDS = set_filters()

    auth = Authorization('https://www.redfin.com')
    auth.start_browser()

    try:
        pages = auth.get_filtered_pages(FILTER_FIELDS)
    except exceptions.NoSuchElementException:
        print('-'*100)
        print(' ' * 4 +'---------------Your IP has been blocked, please reconnect with another IP!---------------')
        print('-'*100)
        return auth.quit_bowser()


    dtmnr = DataMiner()
    page_views = await asyncio.gather(*(dtmnr.get_data(page) for page in pages))

    pagination_urls = (dtmnr.get_each_property_url(page_view) for page_view in page_views)

    async with aiofiles.open(
        file=str(PATH) + "/data.csv", mode="w", 
        encoding="utf-8", newline="") as afp:
        
        writer = AsyncWriter(afp, dialect="unix")
        await writer.writerow(["PropertyAddress", "Zip Code", "Units Total", "Bedrooms Total", "Price for Total Bedrooms", "Unit 1", "Price for Unit 1",  "Unit 2", "Price for Unit 2",  "Unit 3", "Price for Unit 3",  "Unit 4", "Price for Unit 4", ])

        for pagination_url in pagination_urls:
            rows = await asyncio.gather(*(dtmnr.get_property_info(url) for url in tuple(url for url in pagination_url)))
            for row in rows:
                await writer.writerow(row)
    
    auth.quit_bowser()


if __name__ == "__main__":
    asyncio.run(main())


