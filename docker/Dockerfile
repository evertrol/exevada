FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --yes && \
    apt-get upgrade --yes

RUN apt-get install postgis libpq-dev --yes

RUN apt-get install python3-pip --yes

RUN python3 -m pip install Django psycopg2
