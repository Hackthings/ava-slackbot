FROM imageintelligence/python:0d22d56873095d9ef39c6e81d2369a7d3b32300d
MAINTAINER David Vuong <david@imageintelligence.com>

COPY . /root/app
WORKDIR /root/app

RUN make install && make pep

CMD python run.py
