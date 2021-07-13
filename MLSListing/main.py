import csv
import time
import static
import uvloop
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


def get_data(html):
    try:
        soup = BS(html, "html.parser")
    except TypeError:
        elgr.error("Got %s instead of HTML in GET_DATA_FROM_HTML function")
        return {}

    primary_block = soup.find("div", attrs={"id": "PrimaryInfo"})
    property_details = soup.find("div", attrs={"id": "PropertyInfo"})
    construction_info = soup.find("div", attrs={"id": "ConstructionInfo"})
    expenses_and_incomes = soup.find("div", attrs={"id": "ExpensesIncome"})
    property_description = soup.find("div", attrs={"id": "PropertyDescription"})
    tax_information = soup.find("div", attrs={"id": "TaxInfo"})

    output = {}
    raw_data_primary = []
    raw_data_details = []
    raw_data_incomes = []
    raw_roperty_description = []

    if primary_block:
        sub_primary_block = primary_block.find("div", class_="mls-lv-primaryInfo")
        spans = sub_primary_block.find_all("span")

        for span in spans:
            if span.attrs and span.get("class") != ["sr-only"]:
                text = span.text.replace("\n", "").strip()
                if len(text) > 3:
                    raw_data_primary.append(text)

        output["MLS"] = raw_data_primary[0].split()[-2]
        output["Address"] = raw_data_primary[-1]

        if "U:" in output["Address"]:
            output["City"] = output["Address"].split(",")[2].strip()
        else:
            output["City"] = output["Address"].split(",")[1].strip()

        output["ZipCode"] = output["Address"].split()[-1]

        if "$" in raw_data_primary[2]:
            output["ListPrice"] = raw_data_primary[2][1:].replace(",", "")
        else:
            output["ListPrice"] = raw_data_primary[3][1:].replace(",", "")

    if property_details:
        sub_property_details = property_details.find("div", class_="mls-lv-flex-parent")
        spans = sub_property_details.find_all("span")

        for span in spans:
            if span.attrs and span.get("class") != ["sr-only"]:
                text = span.text.replace("\n", "").strip().replace(" ", "")
                if not text.isalpha():
                    raw_data_details.append(text)

        output["TotalUnits"] = raw_data_details[4]
        output["TotalBedrooms"] = raw_data_details[1]
        output["TotalBathrooms"] = raw_data_details[3]

        if "SqFtS" in raw_data_details[8]:
            output["SqFt"] = raw_data_details[8].split("SqFtS")[0].replace(",", "")
        else:
            output["SqFt"] = raw_data_details[7].split("SqFtS")[0].replace(",", "")

        output["TotalMonthlyRent"] = 0

        if len(raw_data_details) == 10:
            output["DaysonMarket"] = raw_data_details[-1].replace(",", "")

        elif len(raw_data_details) == 11:
            output["DaysonMarket"] = raw_data_details[-2].replace(",", "")

        elif len(raw_data_details) == 12:
            output["TotalMonthlyRent"] = (
                raw_data_details[-2].replace("$", "").replace(",", "")
            )
            output["DaysonMarket"] = raw_data_details[-1].replace(",", "")

        else:
            output["TotalMonthlyRent"] = (
                raw_data_details[-3].replace("$", "").replace(",", "")
            )
            output["DaysonMarket"] = raw_data_details[-2].replace(",", "")

    if construction_info:
        sub_construction_info = construction_info.find(
            "div", class_="mls-lv-flex-parent"
        )
        divs = sub_construction_info.find_all("div")

        if len(divs) == 18:
            output["YearBuilt"] = (
                divs[-3].text.split(":")[-1].strip().replace(",", "").replace("\n", "")
            )
        else:
            aprx_year = (
                divs[-2].text.split(":")[-1].strip().replace(",", "").replace("\n", "")
            )

            if aprx_year.isdigit():
                output["YearBuilt"] = aprx_year
            else:
                output["YearBuilt"] = (
                    divs[-4]
                    .text.split(":")[-1]
                    .strip()
                    .replace(",", "")
                    .replace("\n", "")
                )

    output["GrossIncome"] = 0

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
            output["GrossIncome"] = (
                raw_data_incomes[0].replace("$", "").replace(",", "")
            )
        elif len(raw_data_incomes) >= 4:
            output["GrossIncome"] = (
                raw_data_incomes[-4].replace("$", "").replace(",", "")
            )

    if property_description:
        sub_property_description = property_description.find(
            "div", class_="mls-lv-flex-parent"
        )

        spans = sub_property_description.find_all("span")

        for span in spans:
            if span.text.isdigit():
                raw_roperty_description.append(span.text)

        output["TotalParking"] = raw_roperty_description[-1]

    if tax_information:
        sub_tax_information = tax_information.find("div", class_="mls-lv-flex-parent")
        spans = sub_tax_information.find_all("span")

        output["AssessedValue"] = spans[2].text.replace("$", "").replace(",", "")
        output["Tax"] = int(float(spans[6].text.replace("$", "").replace(",", "")))

    return output


async def main():
    current_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
    timeout = aiohttp.ClientTimeout(total=20)

    cookies = await get_cookies()

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
        file=static.PATH + "/outputs/%s_data_.csv" % current_date,
        mode="w",
        encoding="utf-8",
        newline="",
    ) as afp:

        writer = csv.writer(afp, dialect="unix")
        writer.writerow(static.KEYS)

        for url in property_urls:
            property_page = await get_html(session, url)
            hash_data = get_data(property_page)
            dt = Formulas(
                {
                    "price": int(hash_data.get("ListPrice")),
                    "rooms": {
                        int(hash_data.get("TotalUnits")): int(
                            hash_data.get("TotalBedrooms")
                        )
                    },
                    "zip_code": hash_data.get("ZipCode"),
                    "taxes": hash_data.get("Tax"),
                }
            )
            hash_data.update(dt())
            writer.writerow(hash_data.values())
            time.sleep(1.5)

    await session.close()


if __name__ == "__main__":
    elgr = loggers.error_logger()

    uvloop.install()

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    except Exception as e:
        elgr.error(e)
