FROM python:3-alpine

LABEL maintainer="Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>"

RUN apk --update add bash make gcc python3-dev musl-dev libffi-dev openssl-dev

WORKDIR /client

ADD / .

RUN pip install -r requirements.txt && mkdir data

CMD ["bash","/client/docker_conf/init"]
