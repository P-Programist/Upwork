import csv
import json
import time
import datetime as dt

import cloudscraper
from bs4 import BeautifulSoup as BS
from requests.exceptions import ConnectionError as CloudConnectionError

import static
from loggers import custom_logger as cl


class SiteConnector:
    def __init__(self, url) -> None:
        self.url = url
        self.cookies = static.COOKIES

    def get_cookies(self):
        try:
            cookie_request = engine.get(
                url=self.url,
                headers=static.HEADERS,
                cookies=static.COOKIES,
            )
        except CloudConnectionError:
            scrap_err.info(
                "Cookies could not be updated because of the Connection Error, Static Cookies have been used instead"
            )
            return self.cookies

        if cookie_request.cookies:
            self.cookies = cookie_request.cookies
            scrap_err.info("Cookies have been updated")
            return cookie_request.cookies

        scrap_err.info("Static Cookies have been used")

        return self.cookies

    def get_html_page(self, url):
        try:
            html_page_request = engine.get(
                url=url,
                headers=static.HEADERS,
                cookies=self.cookies,
            )
        except CloudConnectionError:
            scrap_err.info(
                "HTML page could not be fetched because of the Connection Error, Static Cookies have been used instead"
            )
            return 0

        if html_page_request.status_code == 200:
            return html_page_request.text

        cl("errors").info(
            "HTML page could not be fetched because of the response %d"
            % html_page_request.status_code
        )
        return 0

    def get_race_venues(self, html):
        if not html:
            scrap_err.error(
                "Could not extract links from %s HTML" % self.url
            )
            return []
        soup = BS(html, "html.parser")

        race_results_window = soup.find("section", attrs={"id": "archiveFormList"})
        if not race_results_window:
            scrap_err.warning(
                "Could not find archiveFormList SECTION window probably because of wrong HTML or there are no races"
            )
            return []

        result_card_sections = race_results_window.find_all("div", class_='w-results-holder')[1:]

        if not result_card_sections:
            scrap_err.warning(
                "Could not find Venues probably because of wrong HTML or there are no races"
            )
            return []

        
        race_links = []

        for result_card_section in result_card_sections:
            sections = result_card_section.find_all('section')

            if '(IRE)' in result_card_section.section.h2.text:
                continue

            for section in sections:
                title_links = section.find_all('a', class_='results-title')

                for title_link in title_links:
                    url = 'https://www.timeform.com' + title_link['href']
                    
                    race_title_text = title_link.text.upper()
                    cleaned_race_definition_word_list = race_title_text.split()

                    if 'HURDLE' in cleaned_race_definition_word_list:
                        race_type_name = 'OTHER HURDLE'
                        if 'HANDICAP' in cleaned_race_definition_word_list:
                            race_type_name = 'HANDICAP HURDLE'
                        elif 'MAIDEN' in cleaned_race_definition_word_list:
                            race_type_name = 'MAIDEN HURDLE'
                        elif 'JUVENILE' in cleaned_race_definition_word_list:
                            race_type_name = 'JUVENILE HURDLE'
                        elif 'NOVICES' in cleaned_race_definition_word_list:
                            race_type_name = 'NOVICES HURDLE'

                    elif 'STAKES' in cleaned_race_definition_word_list:
                        race_type_name = 'OTHER FLAT'
                        if 'MAIDEN' in cleaned_race_definition_word_list:
                            race_type_name = 'MAIDEN STAKES'
                        elif 'NOVICE' in cleaned_race_definition_word_list:
                            race_type_name = 'NOVICE STAKES'
                        elif 'SELLING' in cleaned_race_definition_word_list:
                            race_type_name = 'SELLING STAKES'

                    elif 'HANDICAP' in cleaned_race_definition_word_list:
                        race_type_name = 'HANDICAP'
                        if 'CHASE' in cleaned_race_definition_word_list:
                            race_type_name = 'CHASE HANDICAP'
                        elif 'SELLING' in cleaned_race_definition_word_list:
                            race_type_name = 'SELLING HANDICAP'
                    else:
                        race_type_name = ' '.join(cleaned_race_definition_word_list[-3:-1])

                    race_links.append((url, race_type_name.replace('\'', '')))

        return race_links




class RaceScraper:
    def __init__(self, url, race_type) -> None:
        self.url = url
        self.race_data = []
        self.date_and_time = {}
        self.html = sc.get_html_page(self.url)

        self.race_type = race_type

    def get_race_datetime(self):
        if not self.html:
            scrap_err.error(
                "Could not scrape %s because of broken HTML" % self.url
            )
            return []

        soup = BS(self.html, "html.parser")
        race_header = soup.find("section", attrs={"id": "rp-header"})

        header_rows = race_header.find_all("tr")

        if len(header_rows) < 2:
            scrap_err.warning(
                "Could not fetch DATE and TIME from %s" % self.url
            )
            return []

        race_datetime = header_rows[0].h2.text.split()

        if len(race_datetime) != 5:
            scrap_err.warning(
                "Could not fetch DATE and TIME from %s" % self.url
            )
            return []

        race_time = race_datetime[0]
        race_date_str = " ".join(race_datetime[1:])

        try:
            race_date = dt.datetime.strftime(
                dt.datetime.strptime(
                    race_date_str, "%a %d %B %Y"), "%-d/%-m/%y"
            )
        except ValueError:
            race_date = dt.datetime.strftime(
                dt.datetime.strptime(
                    race_date_str, "%A %d %B %Y"), "%-d/%-m/%y"
            )

        distance_of_the_race = header_rows[1].find_all("td")[-1].text

        self.date_and_time["date"] = race_date
        self.date_and_time["time"] = race_time

        date_and_time_section = soup.find(
            "span", class_='rp-title-course-name')


        if date_and_time_section:    
            self.date_and_time["track"] = date_and_time_section.text.title().strip()
        else:
            title_text = soup.find('h1', class_='rp-title').text
            self.date_and_time["track"] = ' '.join(title_text.split()[:-1]).title().strip()


        self.date_and_time["distance"] = distance_of_the_race.split(
            ":")[-1].strip()

        self.date_and_time["race_type"] = self.race_type

        return self.date_and_time


    def get_race_info_after(self) -> dict:
        if not self.html:
            scrap_err.error(
                "Could not scrape %s because of broken HTML" % self.url
            )
            return []
        soup = BS(self.html, "html.parser")

        main_window = soup.find("div", attrs={"id": "ReportBody"})

        if not main_window:
            scrap_err.warning(
                "Could not find ReportBody on %s because of the race did not start yet" % self.url
            )
            return []

        main_table = main_window.find("table", class_="rp-table rp-results")
        tbodies = main_table.find_all("tbody", class_="rp-table-row")

        local_race_data = None

        for tbody in tbodies:
            local_race_data = {}
            trs = tbody.find_all("tr")


            position = trs[0].find_all(
                "td")[0].find_all("span")[0].text

            local_race_data["position"] = position # Some runners have no number they ended a race

            horse_number_spans = trs[0].find_all(
                "td")[0].find_all("span")
            
            local_race_data["horse_number"] = ''
            if len(horse_number_spans) > 1:
                local_race_data["horse_number"] = horse_number_spans[1].text[1:-1]

            horse_name = trs[0].find_all('td')[4].text.split('.')[-1].strip()
            local_race_data["horse_name"] = horse_name

            jokey = trs[0].find_all('td')[10].text.strip()
            local_race_data["jokey"] = jokey

            trainer = trs[1].find_all('td')[3].text.strip()
            local_race_data["trainer"] = trainer

            horse_age = int(trs[0].find_all('td')[11].text.strip())
            local_race_data["horse_age"] = horse_age

            horse_weight = trs[0].find_all('td')[12].text.strip()
            local_race_data["horse_weight"] = horse_weight

            bsp = trs[0].find_all("td")[15].text.strip()
            local_race_data["bsp"] = float(bsp) if len(bsp) > 0 else 0
            
            bpsp = trs[1].find_all("td")[-1].text.strip()[1:-1]
            local_race_data["bpsp"] = float(bpsp) if len(bpsp) > 0 else 0

            high, low = trs[0].find_all("td")[16].text.strip().split('/')
            local_race_data["high"] = float(high) if high.isdigit() else 0
            local_race_data["low"] = float(low) if low.isdigit() else 0

            B2L = local_race_data["bsp"] - local_race_data["low"]
            local_race_data["B2L"] = B2L

            L2B = local_race_data["high"] - local_race_data["bsp"]
            local_race_data["L2B"] = L2B

            runners = len(tbodies)
            local_race_data["runners"] = runners

            local_race_data.update(self.date_and_time)
            row = tuple(local_race_data.values())
            self.race_data.append(row[14:] + row[:14])

        return local_race_data


    def __call__(self):
        self.get_race_datetime()
        self.get_race_info_after()
        self.race_data.sort(key=lambda x: x[-7], reverse=True)

        return self.race_data


if __name__ == "__main__":
    scrap_err = cl("general")

    engine = cloudscraper.create_scraper()

    count = 0

    for url in static.URLS:
        sc = SiteConnector(url)
        sc.get_cookies()

        html = sc.get_html_page(sc.url)
        all_race_urls = sc.get_race_venues(html)


        with open(
            file=static.PATH + "/csv_data/data%s.csv" % count,
            mode="w",
            encoding="utf-8",
            newline="",
        ) as afp:

            writer = csv.writer(afp, dialect="unix")
            writer.writerow(static.CSV_COLUMNS)

            for r_url in all_race_urls:
                time.sleep(4)

                print(r_url[0],r_url[1])
                ds = RaceScraper(r_url[0],r_url[1])

                result = ds()
                # print(result)
                if result:
                    writer.writerows(result)
                time.sleep(1)
        count += 1

