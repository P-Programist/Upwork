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
from webdriver_manager.chrome import ChromeDriverManager



PATH = pathlib.Path(__file__).parent


# We ask seed of the user to log_in
SEEDS = input('Insert Your seeds(separated by space): ')
PAGE_NUMBER = int(input('How many post do You want to scrape: ')) // 50


class Authorization(object):
    """
    The authorization is the very first step before scraping.
    Due to the Selenium library we sign in on the site and get the list of feed-posts.
    Later, we will pass the PAGE CONTENT to the parser for gathering the data.
    """

    def __init__(self, url):
        super(Authorization, self).__init__()
        self.url = url

        self.chrome_service = Service(ChromeDriverManager().install())
        self.firefox_service = Service(GeckoDriverManager().install())

        self.options = Options()
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")

    def sign_in(self) -> str:
        """
        The module is responsible for two actions:
        1. Insert seeds into the registration field and press log in button.
        2. Click on the "Load More" butten to upload more posts.
        The second step is necessary because of the site is using the lazy loading.
        """

        try:
            self.options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            browser = webdriver.Chrome(options=self.options, service=self.chrome_service)
        except exceptions.WebDriverException:
            try:
                browser = webdriver.Chrome(ChromeDriverManager().install())
            except exceptions.SessionNotCreatedException:
                browser = webdriver.Firefox(service=self.firefox_service)

        browser.maximize_window()

        browser.get(self.url)
        assert 'Welcome to BitClout' in browser.title
        
        time.sleep(10)
        seed_form = browser.find_element(
            By.XPATH,
            "//div[@class='form-group pl-15px pr-15px pt-15px ng-star-inserted']//textarea[@class='form-control fs-15px ng-untouched ng-pristine ng-valid']"
        )
        load_account_btn = browser.find_element(
            By.XPATH,"//button[@class='btn btn-primary font-weight-bold fs-15px']")

        seed_form.click()
        time.sleep(0.5)
        seed_form.send_keys(SEEDS)

        time.sleep(0.5)
        load_account_btn.click()
        time.sleep(10)

        load_more_posts_btn = browser.find_element(
            By.XPATH,"//div[@class='w-100 py-15px d-flex align-items-center justify-content-center cursor-pointer creator-leaderboard__load-more ng-star-inserted']")
        
        interval = 1.8
        for _ in range(PAGE_NUMBER):
            load_more_posts_btn.click()
            time.sleep(interval)
            interval += 0.002

        content = browser.page_source
        browser.quit()
        return content



class BSParser(object):
    """
    This class gets an HTML content as the argument and passes it to its method for further parsing.
    """
    def __init__(self, content):
        super(BSParser, self).__init__()
        self.soup = bs(content, 'html.parser')
        

    async def extract_posts(self) -> str:
        """
        Method is responsible for extracting the data from the HTML content nad write it into csv file.
        """
        feed_posts = self.soup.find_all('feed-post')

        async with aiofiles.open(str(PATH) + '/feed_posts.csv', mode="w", encoding="utf-8") as afp:
            writer = AsyncWriter(afp)
            await writer.writerow(['Author', 'Post'])
            for post in feed_posts:
                author = post.find('a', class_='fc-default font-weight-bold').text.strip()
                text = post.find('div', class_='roboto-regular mt-1').text.strip()
                await writer.writerow([author, text])

        return str(PATH) + 'feed_posts.csv'


if __name__ == "__main__":
    auth = Authorization('https://bitclout.com/log-in')
    content = auth.sign_in()
    bsp = BSParser(content)
    asyncio.run(bsp.extract_posts())
