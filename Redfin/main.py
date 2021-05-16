import asyncio
import pathlib
import time

from aiocsv import AsyncWriter
import aiofiles
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service

from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.chrome import ChromeDriverManager

from


PATH = pathlib.Path(__file__).parent


class Authorization(object):

    def __init__(self, url):
        super(Authorization, self).__init__()
        self.url = url

        # self.chrome_service = Service(ChromeDriverManager().install())
        self.firefox_service = Service(GeckoDriverManager().install())

        self.options = Options()
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")


    def sign_in(self) -> str:

        self.browser = webdriver.Firefox(service=self.firefox_service)
        # self.options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        # self.browser = webdriver.Chrome(options=self.options, service=self.chrome_service)

        # try:
        #     self.options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        #     browser = webdriver.Chrome(options=self.options, service=self.chrome_service)
        # except exceptions.WebDriverException:
        #     pass
            # try:
                # browser = webdriver.Chrome(ChromeDriverManager().install())
            # except exceptions.SessionNotCreatedException:
            #     browser = webdriver.Firefox(service=self.firefox_service)

        self.browser.maximize_window()
        self.browser.get(self.url)
        
        time.sleep(5)


    def make_search(self):
        search_from = self.browser.find_element(
            By.ID,
            "search-box-input"
        )

        search_from.click()
        time.sleep(1)

        search_from.send_keys(search_link)

    def quit_bowser(self):
        return self.browser.quit()



def set_filters():
    DISTRICT = input('What DISTRICT You are looking for (Leave empty and Press Enter -> to skip): ')
    ZIP_CODE = input('What ZIP CODE You are looking for (Leave empty and Press Enter -> to skip): ')
    PROPERTY_TYPE = input('What PROPERTY TYPE You are looking for (Leave empty and Press Enter -> to skip): ')
    MIN_PRICE = input('What MINIMAL PRICE You are looking for (Leave empty and Press Enter -> to skip): ')
    MAX_PRICE = input('What MAXIMUM PRICE You are looking for (Leave empty and Press Enter -> to skip): ')
    MAX_BEDS = input('What MAXIMUM BEDS You are looking for (Leave empty and Press Enter -> to skip): ')
    MIN_BATHROOMS = input('What MINIMAL BATHROOMS You are looking for (Leave empty and Press Enter -> to skip): ')



if __name__ == "__main__":
    auth = Authorization('https://www.redfin.com/')
    content = auth.sign_in()
    auth.quit_bowser()