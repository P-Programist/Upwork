"""
@author: Ilyas Salimov (2020)
This script gets all reviews from all companies in the original data

UPDATE VERSION: Lines 170-172 distinguish this script from the original
                and add the functionality of the review filter until 2020

Input:  Any .xlsx files in the same directory as the script with two required columns: "ID", "Company URL"
Output: The reviews.db database with the reviews table containing all the reviews from companies
        and csv files for each company named "Company ID".csv

Realization: The script is implemented on the "scrapy" framework, all functions and the idea are described on it,
             additional libraries are used for data input and output: "pandas" (for reading xlsx) and "sqlalchemy",
             "csv" (for output to the database and csv files).

             1. Initially, 4 classes are created: item class, table class, pipeline class and spider class.
             2. Using the methods of the spider class described below, the spider receives data (reviews)
             from the site, creates an instance of the item class and returns the data to the pipeline class
             3. Items received by the pipeline create an entry in "reviews.db" and also add an entry to the csv file.
"""

from csv import DictWriter
from re import search, sub
from os import listdir, path
from pathlib import Path

from pandas import read_excel
from sqlalchemy.orm import Session
from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Item, Field, Request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String


PATH = Path(__file__).parent

class ReviewItem(Item):
    """Initialization for a new spider item, creating all fields"""
    company = Field()
    company_id = Field()
    date = Field()
    years_at_company = Field()
    employee_title = Field()
    location = Field()
    employee_status = Field()
    review_title = Field()
    helpful = Field()
    rating_overall = Field()
    rating_balance = Field()
    rating_culture = Field()
    rating_career = Field()
    rating_comp = Field()
    rating_mgmt = Field()
    pros = Field()
    cons = Field()
    rating_diversity = Field()


# Base to create a declarative database, required to create a table class and create a database
Base = declarative_base()


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


class GlassdoorPipeline(object):
    """Pipeline class is used to process the received data"""

    def __init__(self):
        """Initialization of the class in which a declarative database is created"""
        self.engine = create_engine("sqlite:///reviews.db", echo=False)
        Base.metadata.create_all(self.engine)

    def process_item(self, item, spider):
        """Method for adding entries to "reviews.db" and csv file about a new item"""
        fieldnames = ["company", "company_id", "date", "years_at_company", "employee_title", "location",
                      "employee_status", "review_title", "helpful", "rating_overall", "rating_balance",
                      "rating_culture", "rating_career", "rating_comp", "rating_mgmt", "pros", "cons"]
        # Check for file existence to add or not add headers
        is_exist = path.exists(str(item["company_id"]) + ".csv")
        with open(str(item["company_id"]) + ".csv", "a", newline="", encoding="utf-8") as csv_file:
            writer = DictWriter(csv_file, fieldnames=fieldnames)
            if not is_exist:
                writer.writeheader()
            writer.writerow(dict(item))

        data = ReviewsTable(dict(item))
        self.session.add(data)
        self.session.commit()
        return item

    def open_spider(self, spider):
        """The method is called when the spider is opened and creates an active session with the database"""
        self.session = Session(bind=self.engine)

    def close_spider(self, spider):
        """The method is created when the spider is closed and closes the session with the database"""
        self.session.close()


class GlassdoorSpider(Spider):
    """Spider class for retrieving data from a site by making requests."""
    name = "glassdoor"
    review_item = ReviewItem()

    def start_requests(self):
        """Method for sending initial requests for links obtained from xlsx files"""
        urls = []
        for url in get_companies_urls():
            urls.append(url[1].replace("Overview", "Reviews") if "Overview" in url[1]
                        else f"https://www.glassdoor.com/Reviews/{url[1].split('/')[-1]}-Reviews-E{url[0]}.htm")
        for url in urls:
            yield Request(url, callback=self.start_parse)

    def start_parse(self, response):
        """Method for creating and submitting requests to each review page for each company"""
        pages = response.xpath("//div[@class='mt']//strong/text()").get()
        pages = 10 if pages is None else int(pages)
        pages = pages // 10 + 1 if pages % 10 != 0 else pages // 10

        for page in range(1, pages + 1):
            yield Request(response.url.replace(".htm", f"_P{page}.htm"), callback=self.parse,
                          meta={"company_id": search(r"\bE\d+\.htm\b", response.url).group(0)[1:-4]}, dont_filter=True)

    def parse(self, response):
        """Method for parsing the received page (getting all reviews from the page)"""
        company = response.xpath("//span[@id='DivisionsDropdownComponent']/text()").get()
        for review in response.xpath("//li[@class='noBorder empReview cf' or @class='empReview cf']"):
            # The next three lines distinguish this script from the original
            # because they filter out reviews that were later than 2020.
            review_date = review.xpath(".//time[@class='date subtle small']/@datetime").get()
            if int(search(r"\b\d{4}\b", review_date).group(0)) < 2020:
                continue
            helpful = review.xpath(".//div[@class='helpfulReviews helpfulCount small subtle']").get()
            # Further checks are used for the fields "employee title" and "employee status"
            # because not always both are in the review
            employee = review.xpath(".//span[@class='authorJobTitle middle']/text()").get()
            if employee:
                employee = employee.split(" - ") if " - " in employee else ("", employee)
            else:
                employee = ("", "")
            self.review_item["company"] = company
            self.review_item["company_id"] = response.meta["company_id"]
            self.review_item["date"] = review.xpath(".//time[@class='date subtle small']/@datetime").get()
            self.review_item["years_at_company"] = review.xpath(".//p[@class='mainText mb-0']/text()").get()
            self.review_item["location"] = review.xpath(".//span[@class='authorLocation']/text()").get()
            self.review_item["employee_title"] = employee[1]
            self.review_item["employee_status"] = employee[0]
            self.review_item["review_title"] = review.xpath(".//a[@class='reviewLink']/text()").get().replace('"', '')
            self.review_item["helpful"] = search(r"\d+", sub(r"<[^>]*>", "", helpful)).group(0) if helpful else 0
            self.review_item["pros"] = review.xpath(".//p[contains(text(), 'Pros')]/following-sibling::p/text()").get()
            self.review_item["cons"] = review.xpath(".//p[contains(text(), 'Cons')]/following-sibling::p/text()").get()
            self.review_item["rating_overall"] = review.xpath(".//div[@class='v2__EIReviewsRatingsStylesV2__ratingNum "
                                                              "v2__EIReviewsRatingsStylesV2__small']/text()").get()
            self.review_item["rating_balance"] = review.xpath(".//div[contains(text(), 'Work/Life Balance')]"
                                                              "/following-sibling::span/@title").get()
            self.review_item["rating_culture"] = review.xpath(".//div[contains(text(), 'Culture & Values')]"
                                                              "/following-sibling::span/@title").get()
            self.review_item["rating_career"] = review.xpath(".//div[contains(text(), 'Career Opportunities')]"
                                                             "/following-sibling::span/@title").get()
            self.review_item["rating_comp"] = review.xpath(".//div[contains(text(), 'Compensation and Benefits')]"
                                                           "/following-sibling::span/@title").get()
            self.review_item["rating_mgmt"] = review.xpath(".//div[contains(text(), 'Senior Management')]"
                                                           "/following-sibling::span/@title").get()
            yield self.review_item


def get_companies_urls():
    """Function for getting a list of company data"""
    return [item for filename in listdir() if ".xlsx" in filename
            for column in [read_excel(filename)] for item in zip(column["ID"].values.tolist(),
                                                                 column["Company URL"].values.tolist())]


def main():
    """
    The main function of the whole script, creates a process for the spider and starts it unnecessarily in
    the directory with the project

    When creating a process, the following settings are used:
        1) "ROBOTSTXT_OBEY": False - allows the spider to work without the robots.txt bans of the site itself.
        2) "DOWNLOAD_DELAY": 0.1 - sets a delay for receiving data from the site to prevent the captcha.
        3) "ITEM_PIPELINES" - launches a pipeline class for our spider.
        4) "USER_AGENT" - sets a special user agent for requests (optional).
        5) "RETRY_ENABLED": True - turns on the function of retrying requests if the answer is negative.
        6) "RETRY_TIMES": 1000 - determines the number of retries for the previous configuration.
        7) "RETRY_HTTP_CODES" - determines which response codes are considered negative.
    """
    spider = CrawlerProcess({
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 0.1,
        "ITEM_PIPELINES": {
            f"{path.basename(__file__).split('.')[0]}.GlassdoorPipeline": 800
        },
        "USER_AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/81.0.4044.138 Safari/537.36",
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 1000,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 400, 401, 403, 404, 405, 406, 407, 408, 409, 410, 429]
    })
    spider.crawl(GlassdoorSpider)
    spider.start()


# Checking that the script was run directly and not imported
if __name__ == '__main__':
    # main()
    print(get_companies_urls())
    print(listdir(str(PATH)))
