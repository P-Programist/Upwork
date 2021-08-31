import time
import datetime as dt

import requests
import cloudscraper
from bs4 import BeautifulSoup as BS
from requests.exceptions import ConnectionError as CloudConnectionError

import db
from settings import (
    check_db, get_race_type_name,
    DB_TABLE_NAME, CURSOR,
    HEADERS, LOGGER, URL,
    HOME_URL, COOKIES
)


class SiteConnector:
    def __init__(self, url, engine) -> None:
        self.url = url
        self.engine = engine

    def get_html_page(self, url):
        try:
            html_page_request = self.engine.get(
                url=url,
                headers=HEADERS,
                cookies=COOKIES,
                timeout=11
            )
        except CloudConnectionError:
            LOGGER.info(
                "HTML page could not be fetched because of the Connection Error, settings Cookies have been used instead"
            )
            return 0
        except requests.exceptions.ReadTimeout:
            LOGGER.info(
                "The program has freezed and got Timeout Error"
            )
            return {}

        if html_page_request.status_code == 200:
            return html_page_request.text

        LOGGER.info(
            "HTML page could not be fetched because of the response %d"
            % html_page_request.status_code
        )
        time.sleep(10)
        return 0

    def get_race_venues(self, html, today=False) -> list:
        race_links = []

        if not html:
            LOGGER.info("Cannot scrape the HTML for %s" % self.url)
            return race_links

        soup = BS(html, "html.parser")

        if not today:
            race_results_window = soup.find(
                'section', attrs={"id": 'archiveFormList'})
            result_card_sections = race_results_window.find_all(
                'div', class_='w-results-holder')[1:] if race_results_window else []
            ttl_lnk = 'results-title'
        else:
            race_results_window = soup.find('div', class_='w-cards-results')
            result_card_sections = race_results_window.find_all(
                'section') if race_results_window else []
            ttl_lnk = 'w-racecard-grid-race-inactive'

        for result_card_section in result_card_sections:
            if not today:
                sections = result_card_section.find_all('section')
            else:
                sections = result_card_sections

            for section in sections:
                title_links = section.find_all(
                    'a', class_=ttl_lnk) + section.find_all('a', class_='w-racecard-grid-race-result')

                if not today:
                    if section.h2:
                        if 'IRE' in section.h2.text:
                            break
                else:
                    if 'IRE' in section.h3.a.text:
                        break

                for title_link in title_links:
                    url = 'https://www.timeform.com' + title_link['href']

                    if not today:
                        race_title_text = title_link.text.upper()
                    else:
                        race_title_text = title_link['title'].upper()

                    cleaned_race_definition_word_list = race_title_text.split()

                    race_type_name = get_race_type_name(
                        cleaned_race_definition_word_list)

                    race_links.append((url, race_type_name.replace('\'', '')))

        return race_links


class RaceScraper:
    def __init__(self, url) -> None:
        self.url = url
        self.race_data = []
        self.date_and_time = {}

    def get_race_datetime(self, html, race_type):
        if not html:
            LOGGER.error(
                "Could not scrape %s because of broken HTML" % str(html))
            return []

        soup = BS(html, "html.parser")
        race_header = soup.find("section", attrs={"id": "rp-header"})
        header_rows = race_header.find_all("tr")

        if len(header_rows) < 2:
            LOGGER.warning(
                "Could not fetch DATE and TIME from %s" % self.url
            )
            return []

        race_datetime = header_rows[0].h2.text.split()

        if len(race_datetime) != 5:
            LOGGER.warning(
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
            self.date_and_time["track"] = date_and_time_section.text.title(
            ).strip()
        else:
            title_text = soup.find('h1', class_='rp-title').text
            self.date_and_time["track"] = ' '.join(
                title_text.split()[:-1]).title().strip()

        self.date_and_time["distance"] = distance_of_the_race.split(
            ":")[-1].replace('(Inner)', '').replace(' (Old)', '').replace(' (XC)', '').replace(' (New)', '').strip()

        self.date_and_time["race_type"] = race_type

        return self.date_and_time

    def get_race_info_before(self, html) -> dict:
        data_list = []
        soup = BS(html, "html.parser")

        main_window = soup.find("div", attrs={"id": "PassBody"})

        if not main_window:
            LOGGER.warning(
                "Could not find PassBody because of the race did not start yet")
            return []

        main_table = main_window.find("table", attrs={"id": "race-pass-body"})
        tbodies = main_table.find_all("tbody", class_="rp-table-row")

        local_race_data = {}

        runners = len(tbodies)
        local_race_data["runners"] = runners

        local_race_data.update(self.date_and_time)
        row = list(local_race_data.values())
        data_list.append(row[1:] + row[:1])

        return data_list

    def get_race_info_after(self, html) -> dict:
        soup = BS(html, "html.parser")

        main_window = soup.find("div", attrs={"id": "ReportBody"})

        if not main_window:
            LOGGER.warning(
                "Could not find ReportBody on %s because of the race did not start yet" % self.url
            )
            return []

        main_table = main_window.find("table", class_="rp-table rp-results")
        tbodies = main_table.find_all("tbody", class_="rp-table-row")

        for tbody in tbodies:
            local_race_data = {}
            trs = tbody.find_all("tr")

            upper_tds = trs[0].find_all('td')
            lower_tds = trs[1].find_all('td')

            horse_number = trs[0].find_all(
                "td")[0].find_all("span")[0].text

            # Some runners have no number they ended a race
            local_race_data["horse_number"] = horse_number

            position_spans = trs[0].find_all(
                "td")[0].find_all("span")

            local_race_data["position"] = ''
            if len(position_spans) > 1:
                local_race_data["position"] = position_spans[1].text[1:-1]

            horse_name = upper_tds[4].text.split('.')[-1].strip()
            local_race_data["horse_name"] = horse_name

            jokey = upper_tds[10].text.strip()
            local_race_data["jokey"] = jokey

            trainer = lower_tds[3].text.strip()
            local_race_data["trainer"] = trainer

            horse_age = int(upper_tds[11].text.strip())
            local_race_data["horse_age"] = horse_age

            horse_weight = upper_tds[12].text.strip()
            local_race_data["horse_weight"] = horse_weight

            bsp = upper_tds[15].text.strip()
            local_race_data["bsp"] = float(bsp) if len(bsp) > 0 else 0

            bpsp = lower_tds[-1].text.strip()[1:-1]
            local_race_data["bpsp"] = float(bpsp) if len(bpsp) > 0 else 0

            try:
                high, low = trs[0].find_all("td")[16].text.strip().split('/')
            except IndexError:
                LOGGER.critical("Cookies have been expired for %s" % self.url)
                print('\nATTENTION: Your Cookies expired!\nPlease UPDATE cookies!\n')
                exit()

            local_race_data["high"] = float(high) if high.isdigit() else 0
            local_race_data["low"] = float(low) if low.isdigit() else 0

            B2L = local_race_data["bsp"] - local_race_data["low"]
            local_race_data["B2L"] = B2L

            L2B = local_race_data["high"] - local_race_data["bsp"]
            local_race_data["L2B"] = L2B

            runners = len(tbodies)
            local_race_data["runners"] = runners

            local_race_data.update(self.date_and_time)

            row = list(local_race_data.values())
            self.race_data.append(row[14:] + row[:14])

        return local_race_data

    def yesterday_result(self, html, race_type):
        if not self.get_race_datetime(html, race_type):
            return self.race_data

        self.get_race_info_after(html)
        self.race_data.sort(key=lambda x: x[-7])

        return self.race_data


def start_scrape():
    completeness = 1
    today_data_list = []
    yesterday_data_list = []

    engine = cloudscraper.create_scraper()
    site_connector = SiteConnector(URL, engine)

    yesterday_general_html = site_connector.get_html_page(site_connector.url)
    yesterday_all_race_urls = site_connector.get_race_venues(
        yesterday_general_html)

    if not yesterday_general_html:
        LOGGER.error("Could not scrape because of broken HTML")
        print("Could not scrape because of broken HTML")
        exit()

    print('\n\nToday data collection process just started!')
    today_html = site_connector.get_html_page(HOME_URL)
    today_all_race_urls = site_connector.get_race_venues(today_html, True)
    completeness = 1

    for tod_url in today_all_race_urls:
        html = site_connector.get_html_page(tod_url[0])
        if not html:
            continue

        today_instance = RaceScraper(tod_url)
        today_instance.get_race_datetime(html, tod_url[1])
        today_result = today_instance.get_race_info_before(html)

        for row in today_result:
            today_data_list.append(tuple(row))

        done = round(completeness / len(today_all_race_urls) * 100, 2)

        print('Completed {}%'.format(done))

        completeness += 1
        time.sleep(4.7)
    else:
        print('Today data collection process has finished!')

    '''This part is EXTREMELY important, as it check for duplicates, so never remove it from here!'''
    try:
        last_row_list = db.select(
            'date', DB_TABLE_NAME, 'WHERE id = (SELECT MAX(id) FROM %s) LIMIT 1' % DB_TABLE_NAME)
        last_date = last_row_list[0][0]
        instance = RaceScraper(URL)
        instnce_html = site_connector.get_html_page(
            yesterday_all_race_urls[0][0])
        first_race_information = instance.yesterday_result(instnce_html, None)[
            0]

        if last_date in first_race_information:
            print(
                '\nATTENTION: The data might be duplicated, as You scraped the data for today ALREADY!'
            )
            db.db_to_xslx(set(today_data_list))
            exit()
    except IndexError as e:
        print('Database is empty...')

    print('Yesterday data collection process just started...')
    for yes_url in yesterday_all_race_urls:
        yesterday_instance = RaceScraper(yes_url)
        html = site_connector.get_html_page(yes_url[0])

        yesterday_result = yesterday_instance.yesterday_result(
            html, yes_url[1])

        if yesterday_result:
            yesterday_data_list.extend(yesterday_result)

        done = round(completeness / len(yesterday_all_race_urls) * 100, 2)
        print('Completed {}%'.format(done))

        completeness += 1
        time.sleep(4.7)
    else:
        print('Yesterday data collection process has finished!')

    return set(today_data_list), yesterday_data_list


if __name__ == "__main__":
    if check_db() in (1, 2):
        scraped_data = start_scrape()
        db.data_uploader(scraped_data[1])
        db.db_to_xslx(scraped_data[0])

    CURSOR.close()
