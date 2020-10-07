# pull official base image
FROM python:3

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

# set working directory
RUN mkdir /opt/exevada
WORKDIR /opt/exevada

# copy project
COPY . /opt/exevada/

# install dependencies
RUN apt update --yes
RUN apt-get install binutils libproj-dev gdal-bin musl-dev ncat --yes
RUN pip install -r requirements.txt

# entrypoint
ENTRYPOINT ["/opt/exevada/entrypoint.sh"]
