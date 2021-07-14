import csv
import time
import static
import loggers
import asyncio
import aiohttp
import datetime

from bs4 import BeautifulSoup as BS

from excel_formulas import Formulas


async def get_cookies():
    async with aiohttp.ClientSession() as temp_session:
        async with temp_session.get(
            "https://vow.mlspin.com/?cid=6158884&pass=lktdzgly"
        ) as response:
            if response.status == 200:
                return response.cookies


async def get_html(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        else:
            return response.status


def get_property_urls(html):
    try:
        soup = BS(html, "html.parser")
    except TypeError:
        elgr.error("Got %s instead of HTML in GET_DATA_FROM_HTML function")
        return []

    rows = soup.find_all("a", class_="mls-hidden")

    url_list = []

    for row in rows:
        number = row["href"].split("=")[-1]
        url = (
            "https://vow.mlspin.com/VOW/listingviews/GetListing?rm=1&vf=2&summ=false&o=2&od=1&f=0&ps=0&offs=0&sel=%s&sp=false"
            % number
        )
        url_list.append(url)

    return url_list


class Crawler:
    output = {}

    def __init__(self, html) -> None:
        try:
            self.soup = BS(html, "html.parser")
        except TypeError as te:
            elgr.error("Got %s instead of HTML in GET_DATA_FROM_HTML function" % te)
            raise ValueError

    def get_primary_block(self):
        raw_data_primary = []

        primary_block = self.soup.find("div", attrs={"id": "PrimaryInfo"})

        if primary_block:
            sub_primary_block = primary_block.find("div", class_="mls-lv-primaryInfo")
            spans = sub_primary_block.find_all("span")

            for span in spans:
                if span.attrs and span.get("class") != ["sr-only"]:
                    text = span.text.replace("\n", "").strip()
                    if len(text) > 3:
                        raw_data_primary.append(text)

            self.output["MLS"] = raw_data_primary[0].split()[-2]
            self.output["Address"] = raw_data_primary[-1]

            if "U:" in self.output["Address"]:
                self.output["City"] = self.output["Address"].split(",")[2].strip()
            else:
                self.output["City"] = self.output["Address"].split(",")[1].strip()

            self.output["ZipCode"] = self.output["Address"].split()[-1]

            if "$" in raw_data_primary[2]:
                self.output["ListPrice"] = raw_data_primary[2][1:].replace(",", "")
            else:
                self.output["ListPrice"] = raw_data_primary[3][1:].replace(",", "")

        return self.output

    def get_property_details(self):
        raw_data_details = []

        property_details = self.soup.find("div", attrs={"id": "PropertyInfo"})

        if property_details:
            sub_property_details = property_details.find(
                "div", class_="mls-lv-flex-parent"
            )
            spans = sub_property_details.find_all("span")

            for span in spans:
                if span.attrs and span.get("class") != ["sr-only"]:
                    text = span.text.replace("\n", "").strip().replace(" ", "")
                    if not text.isalpha():
                        raw_data_details.append(text)

            self.output["TotalUnits"] = raw_data_details[4]
            self.output["TotalBedrooms"] = raw_data_details[1]
            self.output["TotalBathrooms"] = raw_data_details[3]

            if "SqFtS" in raw_data_details[8]:
                self.output["SqFt"] = (
                    raw_data_details[8].split("SqFtS")[0].replace(",", "")
                )
            else:
                self.output["SqFt"] = (
                    raw_data_details[7].split("SqFtS")[0].replace(",", "")
                )

            self.output["TotalMonthlyRent"] = 0

            if len(raw_data_details) == 10:
                self.output["DaysonMarket"] = raw_data_details[-1].replace(",", "")

            elif len(raw_data_details) == 11:
                self.output["DaysonMarket"] = raw_data_details[-2].replace(",", "")

            elif len(raw_data_details) == 12:
                self.output["TotalMonthlyRent"] = (
                    raw_data_details[-2].replace("$", "").replace(",", "")
                )
                self.output["DaysonMarket"] = raw_data_details[-1].replace(",", "")

            else:
                self.output["TotalMonthlyRent"] = (
                    raw_data_details[-3].replace("$", "").replace(",", "")
                )
                self.output["DaysonMarket"] = raw_data_details[-2].replace(",", "")

        return self.output

    def get_year_built_and_gross_income(self):
        raw_data_incomes = []

        expenses_and_incomes = self.soup.find("div", attrs={"id": "ExpensesIncome"})
        construction_info = self.soup.find("div", attrs={"id": "ConstructionInfo"})

        self.output["GrossIncome"] = 0

        if construction_info:
            sub_construction_info = construction_info.find(
                "div", class_="mls-lv-flex-parent"
            )
            divs = sub_construction_info.find_all("div")

            if len(divs) == 18:
                self.output["YearBuilt"] = (
                    divs[-3]
                    .text.split(":")[-1]
                    .strip()
                    .replace(",", "")
                    .replace("\n", "")
                )
            else:
                aprx_year = (
                    divs[-2]
                    .text.split(":")[-1]
                    .strip()
                    .replace(",", "")
                    .replace("\n", "")
                )

                if aprx_year.isdigit():
                    self.output["YearBuilt"] = aprx_year
                else:
                    self.output["YearBuilt"] = (
                        divs[-4]
                        .text.split(":")[-1]
                        .strip()
                        .replace(",", "")
                        .replace("\n", "")
                    )

        if expenses_and_incomes:
            sub_expenses_and_incomes = expenses_and_incomes.find(
                "div", class_="mls-lv-flex-parent"
            )
            spans = sub_expenses_and_incomes.find_all("span")

            for span in spans:
                if span.attrs and span.get("class") != ["sr-only"]:
                    text = span.text.replace("\n", "").strip().replace(" ", "")
                    if "$" in text:
                        raw_data_incomes.append(text)

            if 1 < len(raw_data_incomes) <= 2:
                self.output["GrossIncome"] = (
                    raw_data_incomes[0].replace("$", "").replace(",", "")
                )
            elif len(raw_data_incomes) >= 4:
                self.output["GrossIncome"] = (
                    raw_data_incomes[-4].replace("$", "").replace(",", "")
                )
        return self.output

    def get_total_parking_tax_and_assesed(self):
        raw_roperty_description = []

        tax_information = self.soup.find("div", attrs={"id": "TaxInfo"})

        property_description = self.soup.find(
            "div", attrs={"id": "PropertyDescription"}
        )

        if property_description:
            sub_property_description = property_description.find(
                "div", class_="mls-lv-flex-parent"
            )

            spans = sub_property_description.find_all("span")

            for span in spans:
                if span.text.isdigit():
                    raw_roperty_description.append(span.text)

            self.output["TotalParking"] = raw_roperty_description[-1]

        if tax_information:
            sub_tax_information = tax_information.find(
                "div", class_="mls-lv-flex-parent"
            )
            spans = sub_tax_information.find_all("span")

            self.output["AssessedValue"] = (
                spans[2].text.replace("$", "").replace(",", "")
            )
            self.output["Tax"] = int(
                float(spans[6].text.replace("$", "").replace(",", ""))
            )
        return self.output

    def get_units_information(self):
        bedrooms_list = []
        bedrooms_table = {}

        unit_information = self.soup.find("div", attrs={"id": "UnitInfo"})

        if not unit_information:
            self.output["UnitCount"] = {0: 0}
            return self.output

        divs = unit_information.find_all(
            "div",
            class_="mls-lv-subsection-header mls-panel-header mls-js-panel-header mls-js-lv-panel-titlebar",
        )
        for div in divs:
            spans = div.find_all("span")
            if len(spans) > 3:
                if spans[6].text.isdigit():
                    bedrooms_list.append(spans[6].text)

        for br in set(bedrooms_list):
            bedrooms_table[bedrooms_list.count(br)] = int(br)

        self.output["UnitCount"] = bedrooms_table

        return self.output

    def __call__(self, *args, **kwds):
        self.get_primary_block()
        self.get_property_details()
        self.get_year_built_and_gross_income()
        self.get_total_parking_tax_and_assesed()
        self.get_units_information()

        return self.output


async def main():
    current_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    timeout = aiohttp.ClientTimeout(total=20)

    try:
        cookies = await get_cookies()
    except aiohttp.client_exceptions.ClientConnectorError as e:
        print("Could not connect to the site %s" % e)
        return elgr.warning("Could not get Cookies %s" % e)

    if not cookies:
        return elgr.warning("Could not get Cookies!")

    session = aiohttp.ClientSession(
        headers=static.HEADERS, timeout=timeout, cookies=cookies
    )

    try:
        main_page = await get_html(
            session, "https://vow.mlspin.com/clients/index.aspx?hpr=y"
        )
    except Exception as e:
        elgr.error(e)
        return 0

    property_urls = get_property_urls(main_page)

    with open(
        file=static.PATH + "/outputs/%s_data.csv" % current_date,
        mode="w",
        encoding="utf-8",
        newline="",
    ) as afp:

        writer = csv.writer(afp, dialect="unix")
        writer.writerow(static.KEYS)
        count = 1
        for url in property_urls:
            print(f"Completed for {round((count / len(property_urls) * 100),2)}% ...")
            count += 1
            property_page = await get_html(session, url)

            hash_data = Crawler(property_page)()
            if not hash_data:
                continue

            dt = Formulas(
                {
                    "price": int(hash_data.get("ListPrice")),
                    "rooms": tuple(hash_data.get("UnitCount").items()),
                    "zip_code": hash_data.get("ZipCode"),
                    "taxes": hash_data.get("Tax"),
                }
            )
            hash_data.update(dt())
            hash_data.pop("UnitCount")
            writer.writerow(hash_data.values())
            time.sleep(2)

    await session.close()


if __name__ == "__main__":
    elgr = loggers.error_logger()

    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())
    # try:
    # except Exception as e:
    #     elgr.error(e)
