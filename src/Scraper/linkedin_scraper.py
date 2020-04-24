import subprocess
import telnetlib
from random import randint
from time import sleep

import chromedriver_binary
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from starlette.responses import JSONResponse
from tldextract import tldextract
from pydantic import BaseModel
from bs4 import BeautifulSoup

from .config import *

app = FastAPI()


def get_url(url):
    return url.replace("https", "http")


@app.get("/")
async def root():
    return {"message": "Welcome to Linkedin Scraper & Email Finder API"}


class EmailFinder(BaseModel):
    company: str
    location: str


@app.post("/linkedin")
async def linkedin_get_company_info_and_recruiter_mails(request: EmailFinder):
    scraper = LinkedinScraper()
    scraper.linkedin_login()
    recruiters = scraper.scrape_recruiters(request.company, request.location)
    if recruiters.__len__() > 0:
        return JSONResponse(content=recruiters)
    else:
        print("No recruiters found")
    scraper.close_scraper()


class LinkedinScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.headless = True
        self.driver = webdriver.Chrome(executable_path=chromedriver_binary.chromedriver_filename,
                                       options=chrome_options)
        self.total_employees_history = []
        self.employees_sum = 0
        self.company_url = ""
        self.mail_format = ""

    def linkedin_login(self):
        self.driver.get(get_url(LINKEDIN_LOGIN_URL))
        self.driver.find_element_by_id(IDS['login_username']).send_keys(CREDENTIALS['email'])
        self.driver.find_element_by_id(IDS['login_password']).send_keys(CREDENTIALS['password'])
        self.driver.find_element_by_css_selector(SELECTORS['login_button']).click()
        print("Successful Linkedin login...")

    def scrape_recruiters(self, company_id, geo_location):
        self.driver.get(
            get_url(LINKEDIN_PEOPLE_LOCATION_FILTER_URL) % {'company': company_id, 'location': geo_location})
        text = self.driver.page_source
        to_crawl = BeautifulSoup(text, "lxml")
        self.get_company_info_and_people(to_crawl)
        company_title = self.convert_company_name(company_id)
        return self.get_recruiters_from_company_people(company_title, geo_location, to_crawl)

    def close_scraper(self):
        self.driver.quit()

    def get_company_info_and_people(self, to_crawl):
        self.company_url = to_crawl.find('a', {'class': CLASSES['company_url']})['href'].strip()
        self.employees_sum = to_crawl.find('span', {'class': CLASSES['employees_number']}).text.strip()
        self.scroll_down_company_people()

    def get_recruiters_from_company_people(self, company_id, geo_location, to_crawl):
        domain = self.extract_domain_from_url(self.company_url)
        mail_server = self.find_mail_server(domain)
        employee_names = to_crawl.findAll('div', {'class': CLASSES['employees_names']})
        employee_urls = to_crawl.findAll('a', {'class': CLASSES['employees_urls']})
        employee_positions = to_crawl.findAll('div', {'class': CLASSES['employees_positons']})
        print("Employees to scrap: %s" % employee_names.__len__())
        recruiters_list = []
        recruiters_number = 0
        print("Ready to discover potential recruiters...")
        for link1, link2, link3 in zip(employee_names, employee_positions, employee_urls):
            name = link1.text
            if name is None:
                continue
            position = link2.text
            profile_url = link3['href']
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
            "recruiters_number": recruiters_number,
            "recruiters": recruiters_list
        }

        json_compatible_item_data = jsonable_encoder(company_info)
        return json_compatible_item_data

    def get_recruiters_info(self, recruiters_list, mail_server, domain):
        if recruiters_list.__len__().__ne__(0):
            self.mail_format = self.get_company_mail_format(recruiters_list[0], mail_server, domain)
            print(self.mail_format)
            for recruiter in recruiters_list:
                first_name = recruiter["name"].split()[0].lower()
                last_name = recruiter["name"].split()[1].lower()
                recruiter['mail'] = self.construct_mail(self.mail_format, first_name, last_name, domain)

    def get_company_mail_format(self, test_recruiter, mail_server, domain):
        mail_dict = self.construct_mail_pool(test_recruiter['name'], "@%s" % domain)
        company_mail_format = self.find_valid_mail_format(mail_dict, mail_server, domain)
        return company_mail_format["format"]

    @staticmethod
    def find_valid_mail_format(mail_dict, mail_server, domain):
        valid_format = None
        print(mail_server)
        with telnetlib.Telnet(mail_server, 25, timeout=10) as session:
            session.set_debuglevel(100)
            sleep(TELNET_RESPONSE_TIME)
            session.read_very_eager()
            # print(b'HELO %s\r\n' % mail_server.encode('ascii'))
            session.write(b'HELO %s\r\n' % mail_server.encode('ascii'))
            sleep(TELNET_RESPONSE_TIME)
            session.read_very_eager()
            # print(response)
            # print(b'MAIL FROM: <info@%s>\r\n' % domain.encode('ascii'))
            session.write(b'MAIL FROM: <info@%s>\r\n' % domain.encode('ascii'))
            sleep(TELNET_RESPONSE_TIME)
            response = session.read_very_eager()
            print(response)
            if response.find(b'OK') > 0 or response.find(b'Ok') > 0:
                for mail in mail_dict.keys():
                    # print(b'RCPT TO: <%s>\n' % mail.encode('ascii'))
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
        self.driver.get(get_url(contact_info_url))
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
