FROM python:3-slim

LABEL maintainer="Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>"

RUN apt-get update && apt-get -y install cron && apt-get clean
WORKDIR /client

ADD / .

RUN pip install -r requirements.txt && mkdir data

CMD ["bash","/client/docker_conf/init"]
