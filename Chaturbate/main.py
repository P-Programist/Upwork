from pathlib import Path
import re, csv, time, datetime

import schedule
import cloudscraper
from random import choice
from bs4 import BeautifulSoup as BS
from requests.exceptions import ConnectionError, InvalidURL

import confs


scraper = cloudscraper.create_scraper()


class Crawler(object):
    def __init__(self, url) -> None:
        super().__init__()
        self.url = url

    def get_cookies(self, proxy: dict):
        try:
            resp = scraper.get(self.url, proxies=proxy)
            if resp.status_code == 200:
                confs.cookies.update(resp.cookies)
                return confs.cookies, resp.text

            elgr.warning(
                f"Response {resp.status_code} from {proxy} during Cookie extraction"
            )
        except ConnectionError:
            elgr.warning("There is no the Internet connection during Cookie extraction")
        except InvalidURL:
            elgr.warning(f"Proxy {proxy} does not work during Cookie extraction")

        return 0

    def get_html(self, cookies: dict, proxy: dict, url: str):
        try:
            time.sleep(2.7)
            resp = scraper.get(url, cookies=cookies, proxies=proxy)
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code == 429:
                elgr.warning(
                    f"Response {resp.status_code} from {proxy} during Getting HTML"
                )
            else:
                elgr.warning(
                    f"{resp.status_code} status code from {proxy} {resp.text.split()[:10]}"
                )
        except ConnectionError:
            elgr.warning("There is no the Internet connection during Getting HTML page")
        except InvalidURL:
            elgr.warning(f"Proxy {proxy} does not work during Getting HTML page")
        return 0

    def get_room_links(self, html):
        try:
            soup = BS(html, "html.parser")
        except TypeError:
            elgr.error(f"Got {html} instead of HTML in GET_ROOM_LINKS function")
            return []
        all_windows = soup.find("ul", attrs={"id": "room_list"})

        if all_windows:
            return tuple(
                self.url + window.find("a")["href"]
                for window in all_windows
                if window.find("a") != -1
            )

        elgr.error(
            f"Could not find any WINDOWS in main page in GET_ROOM_LINKS function"
        )
        return []

    def get_user_data(self, html):
        result = []
        try:
            soup = BS(html, "html.parser")
        except TypeError:
            elgr.error(f"Got {html} instead of HTML in GET_USER_DATA function")
            return result

        username = soup.find("meta", attrs={"property": "og:url"})["content"].split(
            "/"
        )[-2]
        result.append(username)

        attributes = soup.find_all("div", class_="attribute")

        for attribut in attributes:
            label = attribut.find("div", class_="label").text
            data = attribut.find("div", class_="data").text

            if label == "Real Name:":
                result.append(data)

            if label == "I am:":
                data = data.split()[-1]
                result.append(data)
                break

        other_text = soup.find("div", class_="bio")

        if other_text:
            result.append("-".join(extract_email(other_text.text)))
        else:
            result.append(None)
        return result


def extract_email(text):
    return [re_match.group() for re_match in re.finditer(EMAIL_REGEX, text)]


def get_number_of_pages(html):
    soup = BS(html, "html.parser")
    pagination = soup.find("ul", class_="paging")

    if pagination:
        pages = pagination.find_all("li")
        return int(tuple(page.text for page in pages)[-2])

    return -1


def main():
    ilgr.info(f"Test")
    crawler = Crawler("https://chaturbate.com")

    current_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H:%M")
    with open(
        file=PATH + f"/data/data{current_date}.csv",
        mode="w",
        encoding="utf-8",
        newline="",
    ) as afp:

        writer = csv.writer(afp, dialect="unix")
        writer.writerow(["Username", "Gender", "RealName", "Email"])
        proxy = choice(confs.proxies)
        cookies = crawler.get_cookies(proxy)

        if cookies:
            pages = get_number_of_pages(cookies[1])
            if pages == -1:
                pages = 85

            brokens = []

            page_errors_count = 0
            item_errors_count = 0

            for p in range(1, pages + 1):
                if page_errors_count > 10:
                    elgr.error("Too much errors occured!")
                    raise RuntimeError

                proxy = choice(confs.proxies)
                page_data = crawler.get_html(
                    cookies[0], proxy, f"https://chaturbate.com/?keywords=&page={p}"
                )
                if not page_data:
                    page_errors_count += 1
                    brokens.append(f"https://chaturbate.com/?keywords=&page={p}")

                for link in crawler.get_room_links(page_data):
                    if item_errors_count > 13:
                        elgr.error("Too much 429 errors occured!")
                        time.sleep(60)
                        raise ValueError

                    proxy = choice(confs.proxies)
                    html = crawler.get_html(cookies[0], proxy, link)

                    if html:
                        ilgr.info(f"Success from {link} on page {p}")
                        writer.writerow(crawler.get_user_data(html))
                    else:
                        item_errors_count += 1
                time.sleep(15)

            for broken in brokens:
                ilgr.warning(f"{broken} in broken list is trying to re-request")
                proxy = choice(confs.proxies)
                page_data = crawler.get_html(cookies[0], proxy, broken)

                for link in crawler.get_room_links(page_data):
                    proxy = choice(confs.proxies)
                    html = crawler.get_html(cookies[0], proxy, link)
                    if html:
                        ilgr.info(f"Success from {link}")
                        writer.writerow(crawler.get_user_data(html))

                time.sleep(5)
        return -1


if __name__ == "__main__":
    PATH = str(Path(__file__).parent)
    EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    elgr = confs.main_logger()
    ilgr = confs.info_logger()

    schedule.every(3).hours.do(main)

    while True:
        try:
            schedule.run_pending()
        except:
            time.sleep(303)
            pass
        finally:
            time.sleep(10)
