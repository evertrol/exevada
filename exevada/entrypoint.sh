#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DJANGO_HOST $DJANGO_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
#python manage.py collectstatic --noinput
#python manage.py makemigrations exevada
#python manage.py migrate
#python manage.py loaddata stats
#python manage.py runserver localhost:8000
if [ "$DEPLOY" = "1" ]
then
    exec "$@"
else
    exec python manage.py "$@"
fi