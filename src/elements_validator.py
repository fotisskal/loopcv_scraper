import os
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from config import DRIVER_PATH, LINKEDIN_LOGIN_URL, ELEMENT_LOAD_TIME, XPATHS, LINKEDIN_PEOPLE_LOCATION_FILTER_URL


class SeleniumValidator:
    def __init__(self):
        os.chmod(DRIVER_PATH, 0o777)
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        chrome_options = Options()
        chrome_options.headless = True
        self.driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)

    def validate_elements(self, company_id, geo_location):
        try:
            self.driver.get(LINKEDIN_LOGIN_URL)
            self.validate_login_button()
            self.validate_login_button_v2()
            self.driver.get(LINKEDIN_PEOPLE_LOCATION_FILTER_URL % {'company': company_id, 'location': geo_location})
            self.validate_company_url()
            self.validate_company_url_v2()
            self.validate_company_employees()
            self.validate_company_employees_v2()
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_login_button(self):
        try:
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['login_button'])))
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_login_button_v2(self):
        try:
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['login_button_v2'])))
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_company_url(self):
        try:
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['company_url'])))
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_company_url_v2(self):
        try:
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['company_url_v2'])))
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_company_employees(self):
        try:
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['employees_number'])))
        except (TimeoutException, NoSuchElementException):
            raise

    def validate_company_employees_v2(self):
        try:
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['employees_number_v2'])))
        except (TimeoutException, NoSuchElementException):
            raise


if __name__ == '__main__':
    company = sys.argv[1]
    location = sys.argv[2]
    validator = SeleniumValidator()
    validator.validate_elements(company, location)
