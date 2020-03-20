# Introduction
Scraping tool

## PREREQUISITES:

Be sure to have Python v3 installed.

1. Install Selenium
  - pip3 install selenium

2. Install tldextract
  - pip3 install tldextract

3. Install and initiate Mongo DB 4.2
  - pip3 install pymongo
  - brew update
  - brew tap mongodb/brew
  - brew install mongodb-community@4.2
  - brew services start mongodb/brew/mongodb-community

4. Install chromedriver and be sure the binary is in /usr/local/bin path
  - brew cask install chromedriver
  - mv chromedriver /usr/local/bin

> Download options depend on operating system.

## RUNNING:

1. Modify linkedin account CREDENTIALS in config.py (email & password)
2. Execute script linkedin_scraper.py:
  - Command: python3.7 linkedin_scraper.py argumentA argumentB
     - argumentA: the company name as depicted in linkedin company url <br />
        eg. sg-digital-division-of-scientific-games-corporation
     - argumentB: the country location <br />
        eg. Greece
