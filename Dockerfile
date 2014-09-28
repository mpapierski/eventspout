FROM python:2.7.8
MAINTAINER Michał Papierski <michal@papierski.net>

ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
ENTRYPOINT ["python2", "app.py"]