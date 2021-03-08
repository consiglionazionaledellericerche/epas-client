FROM python:3-alpine as builder
LABEL maintainer="Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>"

RUN apk --update add make build-base gcc musl-dev python3-dev libffi-dev openssl-dev cargo
WORKDIR /
COPY requirements.txt .
RUN pip install wheel && mkdir /wheels && pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3-alpine
WORKDIR /client
ADD / .
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt
RUN apk --update add bash && rm -rf /wheels && mkdir /data

CMD ["bash","/client/docker_conf/init"]
