import os
import csv
import json
import asyncio
import aiohttp

from re import search, sub
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


class CompanyInfoExtractor(object):
    def __init__(self) -> None:
        super().__init__()


async def get_page(urls: tuple):
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            response = await session.get(url=url)

            return await response.text()


async def extract_data_from_page(html):
    reviews_json = []
    rates_map = {
        'css-152xdkl': 1,
        'css-19o85uz': 2,
        'css-1ihykkv': 3,
        'css-1c07csa': 4,
        'css-1dc0bv4': 5
    }

    soup = bs(html, 'html.parser')
    reviews_content = soup.find('div', attrs={"id": "ReviewsRef"})
    review_items = reviews_content.find_all('li', class_='noBorder empReview cf pb-0 mb-0')

    # review_item["company"] = company
    # review_item["company_id"] = response.meta["company_id"]


    for item in review_items:
        review_item = {
            "rating_overall": soup.find('div', class_='v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__large').text
        }

        date, employee_title = item.find('span', class_='authorJobTitle middle common__EiReviewDetailsStyle__newGrey').text.split(' - ')
        employee_status, years_at_company = item.find('span', class_='pt-xsm pt-md-0 css-1qxtz39 eg4psks0').text.split(', ')

        location = employee_title.split(' in ')

        # review_title = item.find('a', class_='reviewLink')
        # review_title_link = item.find('a', class_='reviewLink')['href']

        # helpful = item.find('div', class_='common__EiReviewDetailsStyle__socialHelpfulcontainer pt-std')
        # pros, cons = item.find('div', class_='px-std').find_all('p', class_='mt-0 mb-0 pb v2__EIReviewDetailsV2__bodyColor v2__EIReviewDetailsV2__lineHeightLarge v2__EIReviewDetailsV2__isCollapsed  ')
        # rates_block = item.find('aside', class_='gd-ui-tooltip-info toolTip tooltip css-1065bcc').div.div.ul
        # rates = rates_block.find_all('li')


        # review_item["rating_balance"] = rates_map.get(rates[0].find_all('div')[-1]['class'])
        # review_item["rating_culture"] = rates_map.get(rates[1].find_all('div')[-1]['class'])
        # review_item["rating_diversity"] = rates_map.get(rates[2].find_all('div')[-1]['class'])
        # review_item["rating_career"] = rates_map.get(rates[3].find_all('div')[-1]['class'])
        # review_item["rating_comp"] = rates_map.get(rates[4].find_all('div')[-1]['class'])
        # review_item["rating_mgmt"] = rates_map.get(rates[5].find_all('div')[-1]['class'])

        review_item["employee_status"] = employee_status
        review_item["years_at_company"] = years_at_company
        # review_item["review_title"] = review_title
        review_item["date"] = date
        review_item["employee_title"] = employee_title
        review_item["location"] = location
        # review_item["pros"] = pros
        # review_item["cons"] = cons
        
        # review_item["helpful"] = helpful

        reviews_json.append(review_item)
    return reviews_json


if __name__ == "__main__":
    file = get_filename()
    # for row in get_companies_urls(file):
    #     print(row)

    html = asyncio.run(get_page(['https://www.glassdoor.com/Reviews/American-Airlines-Reviews-E8.htm',]))
    data = asyncio.run(extract_data_from_page(html))

    with open(f'{PATH}/test.json', 'w') as test_json:
        json.dump(
            data,
            test_json,
            indent=4,
            ensure_ascii=False
        )


    # Base.metadata.create_all(engine)
    # with Session(engine) as session:
    #     result = session.query(ReviewsTable).all()

    # https://www.glassdoor.com/Overview/Working-at-AAR-EI_IE4.11,14.htm
    # https://www.glassdoor.com/Reviews/AAR-Reviews-E4.htm
    # https://www.glassdoor.com/Reviews/AAR-Reviews-E4_P2.htm
    # https://www.glassdoor.com/Reviews/AAR-Reviews-E4_P3.htm
