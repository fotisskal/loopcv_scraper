LINKEDIN_HOME_URL = 'https://www.linkedin.com'
LINKEDIN_LOGIN_URL = 'https://www.linkedin.com/uas/login'
LINKEDIN_SEARCH_URL = 'https://www.linkedin.com/search/results/all/?keywords=%(company)s%20%(location)s&origin=GLOBAL_SEARCH_HEADER&page=%(page)s'
LINKEDIN_PEOPLE_URL = 'https://www.linkedin.com/company/%s/people/'
LINKEDIN_PEOPLE_LOCATION_FILTER_URL = 'https://www.linkedin.com/company/%(company)s/people/?keywords=%(location)s'

DRIVER_PATH = '/usr/local/bin/chromedriver'

ELEMENT_LOAD_TIME = 6
PAGE_LOAD_TIME = 5
SCROLL_PAUSE_TIME = 4
TELNET_RESPONSE_TIME = 4
TELNET_DELAY_TIME = 5
FILL_BOX_DELAY_TIME = 4

CREDENTIALS = {
    "email": "yyyyy@gmail.com",
    "password": "xxxxx"
}

MAIL_FORMATS = [
    "%(first_name)s%(last_name)s",
    "%(first_name)s.%(last_name)s",
    "%(first_name)s_%(last_name)s",
    "%(first_name)s-%(last_name)s",
    "%(last_name)s%(first_name)s",
    "%(last_name)s.%(first_name)s",
    "%(last_name)s_%(first_name)s",
    "%(last_name)s-%(first_name)s",
    "%(first_name)s",
    "%(last_name)s"
]

XPATHS = {
    "login_username": '//*[@id="username"]',
    "login_password": '//*[@id="password"]',
    "login_button": '//*[@id="app__container"]/main/div/form/div[3]/button',
    "login_button_v2": '//*[@id="app__container"]/main/div/form/div[4]/button',
    "company_url": "/html/body/div[5]/div[4]/div[3]/div/div[3]/section/div/div/div[2]/div[1]/div[2]/div/div/a",
    "company_url_v2": "/html/body/div[6]/div[4]/div[3]/div/div[3]/section/div/div/div[2]/div[1]/div[2]/div/div/a",
    "employees_number": "/html/body/div[5]/div[4]/div[3]/div/div[3]/div/div[2]/div[1]/div[1]/span",
    "employees_number_v2": "/html/body/div[6]/div[4]/div[3]/div/div[3]/div/div[2]/div[1]/div[1]/span",
    "profile_name": "div/section/div/artdeco-entity-lockup/artdeco-entity-lockup-content/artdeco-entity-lockup-title/a/div",
    "position": "div/section/div/artdeco-entity-lockup/artdeco-entity-lockup-content/artdeco-entity-lockup-subtitle/div/div",
    "profile_url": "div/section/div/artdeco-entity-lockup/artdeco-entity-lockup-content/artdeco-entity-lockup-title/a",
    "contact_info": "/html/body/div[4]/div/div/div[2]/section/div/div[1]/div/section[2]/div/a"
}

CLASSES = {
    "company_people": "org-people-profiles-module__profile-list"
}

# Rating [1, 5]
RECRUITMENT_KEYWORDS = {
    "HR": 5,
    "hr": 5,
    "Human Resources": 5,
    "human resources": 5,
    "Director": 3,
    "director": 3,
    "Staff": 5,
    "staff": 5,
    "Staffing": 5,
    "staffing": 5,
    "Talent": 5,
    "talent": 5,
    "People": 4,
    "people": 4
}

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
