import os
import csv
import json
import asyncio
import aiohttp

import re
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from bs4 import BeautifulSoup as bs

PATH = Path(__file__).parent

if os.name == 'posix':
    import uvloop
    uvloop.install()

# Base to create a declarative database, required to create a table class and create a database
Base = declarative_base()

# The engine is responsible for creating local SQLite database next to the executed script.
engine = create_engine(f"sqlite:///{PATH}/reviews.db", echo=False)


class ReviewsTable(Base):
    """Table class for initializing new records and adding rows to the database"""
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    company = Column(String)
    company_id = Column(Integer)
    date = Column(String)
    years_at_company = Column(String)
    employee_title = Column(String)
    location = Column(String)
    employee_status = Column(String)
    review_title = Column(String)
    helpful = Column(String)
    rating_overall = Column(String)
    rating_balance = Column(String)
    rating_culture = Column(String)
    rating_career = Column(String)
    rating_comp = Column(String)
    rating_mgmt = Column(String)
    pros = Column(String)
    cons = Column(String)
    rating_diversity = String()

    def __init__(self, review):
        """Initializing a new record"""
        self.company = review["company"]
        self.company_id = review["company_id"]
        self.date = review["date"]
        self.years_at_company = review["years_at_company"]
        self.employee_title = review["employee_title"]
        self.location = review["location"]
        self.employee_status = review["employee_status"]
        self.review_title = review["review_title"]
        self.helpful = review["helpful"]
        self.rating_overall = review["rating_overall"]
        self.rating_balance = review["rating_balance"]
        self.rating_culture = review["rating_culture"]
        self.rating_career = review["rating_career"]
        self.rating_comp = review["rating_comp"]
        self.rating_mgmt = review["rating_mgmt"]
        self.pros = review["pros"]
        self.cons = review["cons"]

    def __repr__(self):
        """Method for determining the format of outputting data about a class instance (optional)"""
        return "<Review %s %s %s %s %s>" % (self.company_id, self.company, self.date, self.title, self.rating_overall)


def get_filename():
    """Function for getting a list of company data"""
    for f in os.listdir(PATH):
        if ".csv" in f:
            return f
    return input('Provide the ABSOLUTE path to the .CSV file: ')


def get_companies_urls(filename):
    with open(f'{PATH}/{filename}', 'r') as file:
        rows = csv.reader(file)
        return tuple(
            (row[0], row[1], f'{row[-2]},{row[-1]}') for row in rows
        )


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive"
}


async def company_urls(company):
    part_1 = company[-1].split('https://www.glassdoor.com/Overview/Working-at-')[-1]
    company_name = part_1[:part_1.find('-EI')]

    company_reviews_url = f"https://www.glassdoor.com/Reviews/{company_name}-Reviews-E{company[0]}.htm"

    company_reviews_urls = [company_reviews_url,]

    async with aiohttp.ClientSession(headers=headers) as s1:
        response = await s1.get(company_reviews_url)

        html = await response.text()

    page = bs(html, 'html.parser')
    pagination = page.find('div', class_='paginationFooter')

    if pagination:
        from_ = pagination.text.find('of') + 3
        to_ = pagination.text.find('English Reviews')

        users = int(pagination.text[from_:to_].replace(',', ''))
        pages = users // 10 + 1 if users % 10 != 0 else users // 10

        for p in range(2,pages+1):
            company_reviews_urls.append(f"https://www.glassdoor.com/Reviews/{company_name}-Reviews-E{company[0]}_P{p}.htm")

        return company[0], company[1], company_reviews_urls

    return company[0], company[1], company_reviews_url



async def get_page(company: tuple):
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in company[2]:
            response = await session.get(url=url)

            return company[0], company[1], await response.text()


class CompanyInfoExtractor(object):
    def __init__(self, id_, name, html, *args, **kwargs) -> None:
        super(CompanyInfoExtractor, self).__init__(*args, **kwargs)
        self.html = html

        self.company = name
        self.company_id = id_

        self.rates_map = {
            'css-152xdkl': 1,
            'css-19o85uz': 2,
            'css-1ihykkv': 3,
            'css-1c07csa': 4,
            'css-1dc0bv4': 5
        }

        soup = bs(html, 'html.parser')
        self.reviews_content = soup.find('div', attrs={"id": "ReviewsRef"})


    async def extract_data_from_page(self):
        review_items = self.reviews_content.find_all('li', class_='noBorder empReview cf pb-0 mb-0')

        for item in review_items:
            overall = self.soup.find('div', class_='v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__large').text

            review_item = {
                "company": self.company,
                "company_id": self.company_id,
                "rating_overall": overall,
                "rating_balance": 0,
                "rating_culture": 0,
                "rating_diversity": 0,
                "rating_career": 0,
                "rating_comp": 0,
                "rating_mgmt": 0
            }

            date, employee_title = item.find('span', class_='authorJobTitle middle common__EiReviewDetailsStyle__newGrey').text.split(' - ')
            employee_status, years_at_company = item.find('span', class_='pt-xsm pt-md-0 css-1qxtz39 eg4psks0').text.split(', ')

            auth_location = item.find('span', class_='authorLocation')
            location = auth_location.text if auth_location else auth_location

            review_title = item.find('a', class_='reviewLink').text

            helpful_text = re.findall('[0-9]+', item.find('div', class_='common__EiReviewDetailsStyle__socialHelpfulcontainer pt-std').text)

            pros = item.find_all('div', class_='px-std')[-1].find('span', attrs={"data-test": "pros"}).text
            cons = item.find_all('div', class_='px-std')[-1].find('span', attrs={"data-test": "cons"}).text


            rates_block = item.find('ul', class_="pl-0")
            rates = rates_block.find_all('div', attrs={"font-size": "sm"}) if rates_block else 0


            if rates:
                review_item["rating_balance"] = self.rates_map.get(rates[0]['class'][0])
                review_item["rating_culture"] = self.rates_map.get(rates[1]['class'][0])
                review_item["rating_diversity"] = self.rates_map.get(rates[2]['class'][0])
                review_item["rating_career"] = self.rates_map.get(rates[3]['class'][0])
                review_item["rating_comp"] = self.rates_map.get(rates[4]['class'][0])
                review_item["rating_mgmt"] = self.rates_map.get(rates[5]['class'][0])


            review_item["employee_status"] = employee_status
            review_item["years_at_company"] = years_at_company
            review_item["review_title"] = review_title
            review_item["date"] = date
            review_item["employee_title"] = employee_title
            review_item["location"] = location
            review_item["pros"] = pros
            review_item["cons"] = cons
            review_item["helpful"] = helpful_text[0] if helpful_text else 0

            ReviewsTable(review_item)


async def main():
    file = get_filename()
    requests = await asyncio.gather(*(company_urls(company) for company in get_companies_urls(file)[:10]))
    print(requests)
    return requests


if __name__ == "__main__":
    asyncio.run(main())

    # html = asyncio.run(get_page(['https://www.glassdoor.com/Reviews/American-Airlines-Reviews-E8.htm',]))
    # data = asyncio.run(extract_data_from_page(html))

    # while not data:
    #     html = asyncio.run(get_page(['https://www.glassdoor.com/Reviews/American-Airlines-Reviews-E8.htm',]))
    #     data = asyncio.run(extract_data_from_page(html))


    # with open(f'{PATH}/test.json', 'w') as test_json:
    #     json.dump(
    #         data,
    #         test_json,
    #         indent=4,
    #         ensure_ascii=False
    #     )


    # Base.metadata.create_all(engine)
    # with Session(engine) as session:
    #     result = session.query(ReviewsTable).all()