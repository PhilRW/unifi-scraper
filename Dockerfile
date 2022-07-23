FROM python:3.8

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV PROJECT_DIR /usr/local/src/unifi-scraper

WORKDIR ${PROJECT_DIR}

COPY unifi.py ${PROJECT_DIR}

CMD ["python", "unifi.py"]