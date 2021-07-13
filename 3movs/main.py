import gc, os
import time, csv
from random import choice

import cloudscraper
from bs4 import BeautifulSoup as BS
from requests.exceptions import ConnectionError

import configs
from sub_functions import wasabi
from loggers import error_logger, info_logger


class Crawler(object):
    def __init__(self, url) -> None:
        super().__init__()
        self.url = url

    def get_cookies(self, proxy):
        try:
            resp = scraper.get(self.url, headers=configs.headers, proxies=proxy)
            if resp.status_code == 200:
                return resp.cookies
            elgr.warning("Could not get Cookies with %s" % proxy)
        except ConnectionError:
            elgr.warning("There is no the Internet connection...")

        return 0

    def get_html(self, cookies: dict, proxy: dict, url: str, bt=None):
        try:
            time.sleep(3)
            resp = scraper.get(url, cookies=cookies, proxies=proxy)
            if resp.status_code == 200:
                if bt:
                    return resp.content
                return resp.text
        except ConnectionError:
            elgr.warning("There is no the Internet connection...")
        return 0

    def get_video_links(self, html):
        try:
            soup = BS(html, "html.parser")
        except TypeError:
            elgr.error(f"Got {html} instead of HTML in GET_VIDEO_LINKS function")
            raise RuntimeError

        all_items = soup.find_all("div", class_="item")

        try:
            return (item.a["href"] for item in all_items)
        except AttributeError:
            elgr.error("Could not find video link on category page...")
            raise RuntimeError


def get_video_info(html):
    try:
        soup = BS(html, "html.parser")
    except TypeError:
        elgr.error(f"Got {html} instead of HTML in GET_VIDEO_INFO function")
        return {}

    data = {}

    title = soup.find("div", class_="top-heading")
    description = soup.find("p", class_="video_desc")
    download_link = soup.find("a", attrs={"id": "download_link_2"})
    duration = soup.find("ul", class_="tools_info")
    actors = soup.find_all("div", class_="tags")
    tags = soup.find_all("div", class_="tags")
    preview_images = soup.find("div", class_="block-screenshots")

    info_rows = soup.find_all("div", class_="info_row")

    if title:
        data["title"] = title.h2.text
    else:
        data["title"] = soup.find("div", class_="block_header").h1.text

    if description:
        data["description"] = description.text
    else:
        data["description"] = (
            "".join(info_rows[0].text.split(":")[1:])
            .replace("\n", "")
            .replace("\t", "")
        )

    if download_link:
        data["download_link"] = [download_link["href"]]
    else:
        return {}

    if duration:
        data["duration"] = duration.find_all("li")[1].text.split()[-1]
    else:
        data["duration"] = (
            ":".join(info_rows[1].text.split(":")[-2:])
            .replace("\n", "")
            .replace("\t", "")
        )

    if actors:
        data["actors"] = (
            soup.find_all("div", class_="tags")[-1].text.replace("\n", "").strip()
        )
    else:
        data["actors"] = (
            " ".join([actor for actor in info_rows[-2].text.split(":")[1:]])
            .replace("\n", "")
            .strip()
        )

    if tags:
        data["tags"] = tags[0].text.replace("\n", " ").strip()
    else:
        data["tags"] = ",".join([tag.text for tag in info_rows[2].find_all("a")])

    if preview_images:
        raw_preview_images = preview_images.find_all("img")
        data["preview_images"] = [image["src"] for image in raw_preview_images]
    else:
        data["preview_images"] = [soup.find("video", class_="player")["poster"]]

    return data


def get_number_of_pages(html):
    try:
        soup = BS(html, "html.parser")
    except TypeError:
        elgr.error(f"Got {html} instead of HTML in GET_NUMBER_OF_PAGES function")
        return 99999

    pagination = soup.find("div", class_="block_sub_header p-ig")

    if pagination:
        pages_list = pagination.find_all("a")
        max_page = pages_list[-2].text
        return int(max_page)

    return 99999


def executor(crawler: Crawler, category: str, proxy: str, cookie: dict):
    category_html = crawler.get_html(cookie, proxy, crawler.url + f"/{category}/")
    category_name = category.split("/")[-1]

    total_pages = get_number_of_pages(category_html)

    with open(
        file=configs.PATH + f"/data/{category_name}_data.csv",
        mode="w",
        encoding="utf-8",
        newline="",
    ) as afp:
        writer = csv.writer(afp, dialect="unix")
        writer.writerow(
            [
                "Title",
                "Description",
                "Duration",
                "Actors",
                "Tags",
                "PreviewImage1",
                "PreviewImage2",
                "PreviewImage3",
                "PreviewImage4",
                "PreviewImage5",
                "PreviewImage6",
                "PreviewImage7",
                "PreviewImage8",
                "PreviewImage9",
                "PreviewImage10",
                "Video",
            ]
        )

        for pg in range(1, total_pages + 1):
            category_page_html = crawler.get_html(
                cookie, proxy, crawler.url + f"/{category}/{pg}/"
            )

            if not category_page_html:
                raise ValueError

            video_links = crawler.get_video_links(category_page_html)

            for video_link in video_links:
                row = []
                proxy = choice(configs.proxies)
                v_link = video_link.replace("m.3movs.com", "www.3movs.com")
                html_pg = crawler.get_html(cookie, proxy, v_link)
                data = get_video_info(html_pg)

                if not data or len(data.get("preview_images", [])) < 2:
                    elgr.error("Broken HTML returned from %s " % v_link)
                    raise ValueError

                row.extend(list(data.values())[:-2])
                gc.collect()

                for img_url in data["preview_images"]:
                    wasabi(
                        crawler.get_html(cookie, proxy, img_url, bt=True),
                        img_url,
                        "photo",
                    )

                video_url = data.get("download_link")[0]

                wasabi(
                    crawler.get_html(cookie, proxy, video_url, bt=True),
                    video_url,
                    "video",
                )
                ilgr.info("Data successfully collected from %s" % video_link)

                writer.writerow(row)


def main():
    crawler_instance = Crawler("https://www.3movs.com")

    categories = [
        "tags/standing",
        "categories/anal",
    ]

    for category in categories:
        proxy = choice(configs.proxies)
        cookie = crawler_instance.get_cookies(proxy)
        if cookie:
            executor(crawler_instance, category, proxy, cookie)


if __name__ == "__main__":
    elgr = error_logger()
    ilgr = info_logger()

    scraper = cloudscraper.create_scraper()

    while True:
        try:
            main()
        except Exception as e:
            elgr.info("Script got Exception")
            break
    os.system("service restart 3movs")
