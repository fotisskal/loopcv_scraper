FROM python:3-buster

WORKDIR /usr/src/app

COPY src/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
    sudo apt-get install -y unzip
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb
    wget -N https://chromedriver.storage.googleapis.com/80.0.3987.16/chromedriver_linux64.zip -P ~/
    unzip ~/chromedriver_linux64.zip -d ~/
    rm ~/chromedriver_linux64.zip
    sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
    sudo chown root:root /usr/local/bin/chromedriver
    sudo chmod 0755 /usr/local/bin/chromedriver

COPY loopcv_scraper .

EXPOSE 8000