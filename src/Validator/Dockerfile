FROM python:3-buster

WORKDIR /usr/src/app

COPY src/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb

COPY src/Validator .

EXPOSE 8000

CMD ["uvicorn", "Validator/elements_validator:app", "--port", "8000", "--reload"]