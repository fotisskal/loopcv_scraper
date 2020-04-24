from unittest import TestCase

from src.Scraper.linkedin_scraper import LinkedinScraper


class TestLinkedinScraper(TestCase):

    def setUp(self):
        self.scraper = LinkedinScraper()


class TestA(TestLinkedinScraper):
    def test_get_mail_from_linkedin_profile(self):
        self.scraper.linkedin_login()
        mail = self.scraper.get_mail_from_linkedin_profile("https://www.linkedin.com/in/fotis-kalathopoulos-58719186")
        self.assertEqual(mail, 'fotis.kal21@gmail.com')


class TestB(TestLinkedinScraper):
    def test_construct_mail_pool(self):
        mail_list = self.scraper.construct_mail_pool('Fotis Kalathop', '@niometrics.com')
        print(mail_list)
        self.assertEqual(mail_list.__len__(), 400)


class TestC(TestLinkedinScraper):
    def test_find_valid_mail(self):
        mail_list = ['katsoulis@navarino.gr']
        valid_mail = self.scraper.find_valid_mail_format(mail_list, 'navarino-gr.mail.protection.outlook.com',
                                                         'navarino.gr')
        print(valid_mail)
        # self.assertEqual(valid_mail, 'kalathopoulos@niometrics.com')


class TestD(TestLinkedinScraper):
    def test_linkedin_login(self):
        self.scraper.linkedin_login()
        self.scraper.get_company_info_and_people('niometrics', 'Greece')
        print(self.scraper.driver.page_source)


class TestE(TestLinkedinScraper):
    def test_get_recruiters(self):
        self.scraper.linkedin_login()
        self.scraper.get_company_info_and_people('sg-digital-division-of-scientific-games-corporation', 'Greece')
        print(self.scraper.get_recruiters_from_company_people('sg-digital', 'Greece'))


class TestF(TestLinkedinScraper):
    def test_get_company_url_and_people_number(self):
        self.scraper.linkedin_login()
        self.scraper.get_company_info_and_people('niometrics', 'Greece')
        self.assertEqual(self.scraper.get_company_url(), 'https://www.niometrics.com/')
        self.assertEqual(self.scraper.get_employees_number(), '36')


class TestG(TestLinkedinScraper):
    def test_get_company_people_list(self):
        self.scraper.linkedin_login()
        self.scraper.get_company_info_and_people('niometrics', 'Greece')
        employee_list = self.scraper.get_employees_list()
        employees = employee_list.find_elements_by_tag_name('li')
        self.assertEqual(employees.__len__(), '36')


class TestH(TestLinkedinScraper):
    def test_create_company_name(self):
        print(self.scraper.convert_company_name('sg-digital-division-of-scientific-games-corporation'))


class TestI(TestLinkedinScraper):
    def test_page_source(self):
        self.scraper.linkedin_login()
        self.scraper.get_company_info_and_people('niometrics', 'Greece')
        html_source = self.scraper.driver.page_source
        print(html_source)

