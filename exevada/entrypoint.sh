#!/bin/bash

#python manage.py collectstatic --noinput
#python manage.py loaddata stats
python manage.py makemigrations exevada
python manage.py migrate
python manage.py runserver 0.0.0.0:8000