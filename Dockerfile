FROM python:3-slim

LABEL maintainer="Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>"

WORKDIR /client

ADD / .

RUN pip install -r requirements.txt && mkdir data

CMD ["bash","/client/docker_conf/init"]
