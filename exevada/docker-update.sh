#!/usr/bin/env bash

# bash script to rebuild django container and apply migrations 
# to be used in production mode when frontend or db model changes
# have been pulled from the repo

git pull

docker-compose -f docker-compose-prod.yml up -d --no-deps --build web
docker-compose exec web python manage.py makemigrations exevada
docker-compose exec web python manage.py migrate exevada
