FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /opt/exevada
WORKDIR /opt/exevada
COPY . /opt/exevada/
RUN apt update --yes
RUN apt-get install binutils libproj-dev gdal-bin --yes
RUN pip install -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py loaddata stats