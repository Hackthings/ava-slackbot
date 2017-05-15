FROM python:3.6-alpine
MAINTAINER David Vuong <david@imageintelligence.com>

COPY . /root/app
WORKDIR /root/app

RUN pip install -r requirements.txt && pep8 ./ --ignore=E501,E701
CMD python run.py
