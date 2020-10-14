# pull official base image
FROM python:3

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

# set working directory
RUN mkdir /opt/exevada
WORKDIR /opt/exevada

# copy project
COPY ./apps/ /opt/exevada/apps/
COPY ./entrypoint.sh /opt/exevada/entrypoint.sh
COPY ./manage.py /opt/exevada/manage.py
COPY ./project/ /opt/exevada/project/
COPY ./requirements.txt /opt/exevada/requirements.txt
COPY ./wsgi.py /opt/exevada/wsgi.py

# copy wordpress files
# COPY ./wp-content/ /opt/exevada/project/static/wp-content/

# install dependencies
RUN apt update --yes
RUN apt-get install binutils libproj-dev gdal-bin musl-dev ncat --yes
RUN pip install -r requirements.txt

# entrypoint
ENTRYPOINT ["/opt/exevada/entrypoint.sh"]
