import os
import sys

from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options

from src.Scraper.linkedin_scraper import get_url
from .config import *

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to Linkedin Scraper & Email Finder API"}


class ValidatorParams(BaseModel):
    company: str
    location: str


@app.post("/linkedin")
async def linkedin_get_company_info_and_recruiter_mails(request: ValidatorParams):
    try:
        validator = SeleniumValidator()
        validator.validate_elements(request.company, request.location)
    except (TimeoutException, NoSuchElementException):
        raise


class SeleniumValidator:
    def __init__(self):
        os.chmod(DRIVER_PATH, 0o777)
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        chrome_options = Options()
        chrome_options.headless = True
        self.employees_sum = 0
        self.company_url = ""
        self.mail_format = ""
        self.driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)

    def validate_elements(self, company_id, geo_location):
        try:
            self.driver.get(get_url(LINKEDIN_LOGIN_URL))
            self.validate_login_button()
            self.driver.get(
                get_url(LINKEDIN_PEOPLE_LOCATION_FILTER_URL) % {'company': company_id, 'location': geo_location})
            text = self.driver.page_source
            to_crawl = BeautifulSoup(text, "lxml")
            self.validate_company_url(to_crawl)
            self.validate_company_employees(to_crawl)
            self.validate_employees(to_crawl)
            self.driver.close()
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_login_button(self):
        try:
            self.driver.find_element_by_css_selector(SELECTORS['login_button']).click()
        except (TimeoutException, NoSuchElementException):
            raise

    @staticmethod
    def validate_company_url(to_crawl):
        try:
            to_crawl.find('a', {'class': CLASSES['company_url']})['href'].strip()
        except (TimeoutException, NoSuchElementException):
            raise

    @staticmethod
    def validate_company_employees(to_crawl):
        try:
            to_crawl.find('span', {'class': CLASSES['employees_number']}).text.strip()
        except (TimeoutException, NoSuchElementException):
            raise

    @staticmethod
    def validate_employees(to_crawl):
        try:
            to_crawl.findAll('div', {'class': CLASSES['employees_names']})
            to_crawl.findAll('a', {'class': CLASSES['employees_urls']})
            to_crawl.findAll('div', {'class': CLASSES['employees_positons']})
        except (TimeoutException, NoSuchElementException):
            raise
