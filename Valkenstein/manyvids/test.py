import re
import multiprocessing
import csv
import random

import configs
import datetime

from bs4 import BeautifulSoup as BS
from requests.exceptions import ConnectionError

import aiohttp
import asyncio


class Scraper:
    def __init__(self, url):
        self.url = url
        self.cookies = configs.COOKIES

    async def get_cookies(self):
        async with aiohttp.ClientSession() as temp_session:
            async with temp_session.get(self.url) as response:
                if response.status == 200:
                    self.cookies.update(response.cookies)
                    return self.cookies
                return self.cookies

    async def get_html(self, session: aiohttp.ClientSession, url: str):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return 0
        except ConnectionError:
            return 0

    async def amount_of_pages(self, session):
        html = await self.get_html(session, self.url)
        try:
            soup = BS(html, "html.parser")
            paginatoin = soup.find("span", class_="page-total")
            return int(paginatoin.text)
        except:
            return 0

    async def get_links(self, session, page):
        page_url = (
            "https://www.manyvids.com/MVGirls/?page=%s&search_type=0&sort=1&type_id=1"
            % page
        )

        html = await self.get_html(session, page_url)

        if not html:
            return []

        soup = BS(html, "html.parser")
        link_blocks = soup.find_all("div", class_="relative")

        return [
            block_link.a["href"].replace("Store/Videos/", "About/")
            for block_link in link_blocks
        ]

    async def collect_data(self, sessions, pages):
        date_name = str(
            datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H:%M")
        )

        with open(configs.PATH + f"/data/{date_name}_report.csv", "w") as csvfile:
            wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            wr.writerow(["Username", "Email"])

            for page in range(204, pages + 1):
                session = random.choice(sessions)
                await self.get_cookies()

                links = await self.get_links(session, page)

                links_data = await asyncio.gather(
                    *(self.get_html(random.choice(sessions), link) for link in links)
                )

                for ld in links_data:
                    soup = BS(ld, "html.parser")
                    user = soup.find("h2", class_="mv-about__banner-name")
                    email_in_text = soup.find(
                        "div", class_="mv-about__container__description"
                    )

                    if email_in_text:
                        email_str = email_in_text.text
                        an_email = "".join(
                            re.findall(
                                "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
                                email_str,
                            )
                        )
                        if an_email:
                            wr.writerow([user.text, an_email])


async def main():
    timeout = aiohttp.ClientTimeout(total=20)

    sessions = [
        aiohttp.ClientSession(
            timeout=timeout,
            cookies=configs.COOKIES,
            connector=aiohttp.TCPConnector(ssl=False),
            trust_env=True,
            headers=configs.HEADERS,
        )
        for _ in range(15)
    ]

    for url in configs.URLS:
        scp = Scraper(url)
        await scp.get_cookies()
        pages = await scp.amount_of_pages(sessions[0])

        if pages:
            print(pages)
            task = asyncio.create_task(scp.collect_data(sessions, pages))
            asyncio.ensure_future(task)

    for session in sessions:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
