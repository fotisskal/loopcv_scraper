import json
import subprocess
import sys
import telnetlib
from random import randint
from time import sleep

import chromedriver_binary
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from tldextract import tldextract

from .config import *


class LinkedinScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.headless = True
        self.driver = webdriver.Chrome(executable_path=chromedriver_binary.chromedriver_filename, options=chrome_options)
        self.total_employees_history = []
        self.employees_sum = 0
        self.company_url = ""
        self.mail_format = ""

    def linkedin_login(self):
        self.driver.get(LINKEDIN_LOGIN_URL)
        try:
            login_button = XPATHS['login_button']
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, login_button)))
        except (TimeoutException, NoSuchElementException):
            login_button = self.linkedin_login_v2()
            pass
        self.driver.find_element_by_xpath(XPATHS['login_username']).send_keys(CREDENTIALS['email'])
        self.driver.find_element_by_xpath(XPATHS['login_password']).send_keys(CREDENTIALS['password'])
        self.driver.find_element_by_xpath(login_button).click()
        print("Successful Linkedin login...")

    def linkedin_login_v2(self):
        print("Check alternative xpath for login button")
        login_button = XPATHS['login_button_v2']
        WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
            expected_conditions.visibility_of_element_located((By.XPATH, login_button)))
        return login_button

    def scrape_recruiters(self, company_id, geo_location):
        self.get_company_info_and_people(company_id, geo_location)
        company_title = scraper.convert_company_name(company_id)
        return self.get_recruiters_from_company_people(company_title, geo_location)

    def close_scraper(self):
        self.driver.quit()

    def get_company_info_and_people(self, company_id, geo_location):
        self.driver.get(LINKEDIN_PEOPLE_LOCATION_FILTER_URL % {'company': company_id, 'location': geo_location})
        self.company_url = self.get_company_url()
        self.employees_sum = self.get_employees_number()
        self.scroll_down_company_people()

    def get_recruiters_from_company_people(self, company_id, geo_location):
        domain = self.extract_domain_from_url(self.company_url)
        mail_server = self.find_mail_server(domain)
        employee_list = self.get_employees_list()
        employees = employee_list.find_elements_by_tag_name('li')
        print("Employees to scrap: %s" % employees.__len__())
        recruiters_list = []
        recruiters_number = 0
        print("Ready to discover potential recruiters...")
        for employee in employees:
            name = self.get_employee_name(employee)
            if name is None:
                continue
            position = self.get_employee_position(employee)
            profile_url = self.get_employee_url(employee)
            for key in RECRUITMENT_KEYWORDS.keys():
                if key in position:
                    print("Recruiter: %s" % name)
                    recruiters_number += 1
                    recruiters_list.append({
                        "name": name,
                        "position": position,
                        "profile_url": profile_url,
                        "rating": RECRUITMENT_KEYWORDS[key]
                    })
                    break
        self.get_recruiters_info(recruiters_list, mail_server, domain)

        company_info = {
            "name": company_id,
            "location": geo_location,
            "url": self.company_url,
            "domain": domain,
            "mail_server": mail_server,
            "mail_format": self.mail_format,
            "employees_number": self.employees_sum,
            "recruiters_number": recruiters_number
        }
        print(json.dumps(company_info, indent=2))
        return recruiters_list

    def get_company_url(self):
        try:
            company_url_xpath = XPATHS['company_url']
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, company_url_xpath)))
        except (TimeoutException, NoSuchElementException):
            company_url_xpath = self.get_company_url_v2()
            pass
        return self.driver.find_element_by_xpath(company_url_xpath).get_attribute('href').strip()

    def get_company_url_v2(self):
        print("Check alternative xpath for company url")
        company_url_xpath = XPATHS['company_url_v2']
        WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
            expected_conditions.visibility_of_element_located((By.XPATH, company_url_xpath)))
        return company_url_xpath

    def get_employees_number(self):
        try:
            company_workforce_xpath = XPATHS['employees_number']
            WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
                expected_conditions.visibility_of_element_located((By.XPATH, company_workforce_xpath)))
        except (TimeoutException, NoSuchElementException):
            company_workforce_xpath = self.get_employees_number_v2()
            pass
        return self.driver.find_element_by_xpath(company_workforce_xpath).get_attribute("innerHTML").strip().split()[0]

    def get_employees_number_v2(self):
        print("Check alternative xpath for company employees number")
        company_workforce_xpath = XPATHS['employees_number_v2']
        WebDriverWait(self.driver, ELEMENT_LOAD_TIME).until(
            expected_conditions.visibility_of_element_located((By.XPATH, company_workforce_xpath)))
        return company_workforce_xpath

    def get_employees_list(self):
        return self.driver.find_element_by_class_name(CLASSES['company_people'])

    @staticmethod
    def get_employee_name(employee):
        try:
            employee_name = employee.find_element_by_xpath(XPATHS['profile_name']).text
        except NoSuchElementException:
            return None
        return employee_name

    @staticmethod
    def get_employee_position(employee):
        return employee.find_element_by_xpath(XPATHS['position']).text

    @staticmethod
    def get_employee_url(employee):
        return employee.find_element_by_xpath(XPATHS['profile_url']).get_attribute('href')

    def get_recruiters_info(self, recruiters_list, mail_server, domain):
        # recruiter_mail = self.get_mail_from_linkedin_profile(recruiter['profile_url'])
        # if recruiter_mail is None:
        if recruiters_list.__len__().__ne__(0):
            self.mail_format = self.get_company_mail_format(recruiters_list[0], mail_server, domain)
            for recruiter in recruiters_list:
                first_name = recruiter["name"].split()[0].lower()
                last_name = recruiter["name"].split()[1].lower()
                recruiter['mail'] = self.construct_mail(self.mail_format, first_name, last_name, domain)
            self.store_to_mongo_db("recruiters", recruiters_list)

    def get_company_mail_format(self, test_recruiter, domain, mail_server):
        mail_dict = self.construct_mail_pool(test_recruiter['name'], "@%s" % domain)
        company_mail_format = self.find_valid_mail_format(mail_dict, mail_server, domain)
        return company_mail_format["format"]

    @staticmethod
    def find_valid_mail_format(mail_dict, mail_server, domain):
        valid_format = None
        with telnetlib.Telnet(mail_server, 25, timeout=10) as session:
            sleep(TELNET_RESPONSE_TIME)
            session.read_very_eager()
            for mail in mail_dict.keys():
                print(b'HELO %s\r\n' % mail_server.encode('ascii'))
                session.write(b'HELO %s\r\n' % mail_server.encode('ascii'))
                sleep(TELNET_RESPONSE_TIME)
                session.read_very_eager()
                print(b'MAIL FROM: <info@%s>\r\n' % domain.encode('ascii'))
                session.write(b'MAIL FROM: <info@%s>\r\n' % domain.encode('ascii'))
                sleep(TELNET_RESPONSE_TIME)
                response = session.read_very_eager()
                print(response)
                if response.find(b'OK') > 0 or response.find(b'Ok') > 0:
                    print(b'RCPT TO: <%s>\n' % mail.encode('ascii'))
                    session.write(b'RCPT TO: <%s>\r\n' % mail.encode('ascii'))
                    sleep(TELNET_RESPONSE_TIME)
                    response = session.read_very_eager()
                    print(response)
                    if response.find(b'OK') > 0 or response.find(b'Ok') > 0:
                        valid_format = mail_dict[mail]
                        break
                    elif response.find(b'550 5.7.606') > 0:
                        raise Exception(response)
                sleep(TELNET_DELAY_TIME)
        return valid_format

    @staticmethod
    def find_mail_server(domain):
        out = subprocess.Popen(['dig', '+answer', '+short', 'mx', domain],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        stdout = out.communicate()
        mail_server = stdout[0].decode("utf-8").split()[1][:-1]
        return mail_server

    def construct_mail_pool(self, name, domain):
        mail_map = {}
        first_name = name.split()[0].lower()
        last_name = name.split()[1].lower()
        for f_range in range(len(first_name), 0, -1):
            for l_range in range(len(last_name), 0, -1):
                for mail_format in MAIL_FORMATS:
                    email = self.construct_mail(mail_format, first_name[0:f_range], last_name[0:l_range], domain)
                    mail_map[email] = {
                        "format": mail_format,
                        "indexes": (f_range, l_range)
                    }
        return mail_map

    @staticmethod
    def construct_mail(mail_format, first_name, last_name, domain):
        return mail_format % {'first_name': first_name, 'last_name': last_name} + "%s" % domain

    # Issue: may not be feasible if profile not connected with recruiter because of privacy settings
    def get_mail_from_linkedin_profile(self, profile_url):
        contact_info_url = profile_url + "/detail/contact-info/"
        self.driver.get(contact_info_url)
        mail = self.get_mail_if_present()
        return mail

    def get_mail_if_present(self):
        try:
            mail = self.driver.find_element_by_xpath(XPATHS['contact_info']).get_attribute("innerHTML").strip()
        except NoSuchElementException:
            return None
        return mail

    def scroll_down_company_people(self):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, (document.body.scrollHeight));")
            # Wait to load page
            sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            self.random_scroll_up(10)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.random_scroll_up(last_height)
                break
            last_height = new_height

    def random_scroll_up(self, height):
        random_height = randint(0, height)
        self.driver.execute_script("window.scrollTo(%s, 0);" % random_height)

    @staticmethod
    def extract_domain_from_url(url):
        return tldextract.extract(url).registered_domain

    @staticmethod
    def convert_company_name(linkedin_company):
        return linkedin_company.replace("-", " ").title()


if __name__ == '__main__':
    company = sys.argv[1]
    location = sys.argv[2]
    scraper = LinkedinScraper()
    scraper.linkedin_login()
    recruiters = scraper.scrape_recruiters(company, location)
    if recruiters.__len__() > 0:
        print(json.dumps(recruiters, indent=2))
    else:
        print("No recruiters found")
    scraper.close_scraper()
