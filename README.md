# Introduction
Scraping tool for Linkedin with the ultimate purpose to filter out recruiters and find their e-mails
based on the company name and a location.

## RUNNING:

1. Modify linkedin account CREDENTIALS in config.py (email & password)
2. Inside loopcv_scraper:

       - docker build -f Dockerfile.Scraper --tag Scraper:1.0 .
       
       - docker build -f Dockerfile.Validator --tag Validator:1.0 .
       
       - docker run --publish 8000:8000 --detach --name scr Scraper:1.0
       
       - docker run --publish 8000:8000 --detach --name val Validator:1.0
       
    - Hit browser: http://127.0.0.1:8000/docs
   
   > Notes
   >- publish: forward traffic incoming on the host’s port 8000, to the container’s ports 8000 and 8080.
   >- detach: run this container in the background.
   >- name: specifies a name with which you can refer to your container in subsequent commands.
