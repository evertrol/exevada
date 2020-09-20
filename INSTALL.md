# Install Guide
In the following instructions we assume you have cloned the repository to your local hard drive:
```shell
$ git clone git@github.com:C3S-attribution-service/exevada.git
$ cd exevada/exevada
```
## Linux local installation
### Python dependencies
We have included a set of required python-3 packages in `requirements.txt`. You can optionally create a virtual environment to contain them, and run
```shell
pip install -r requirements.txt
```
### PostgreSQL with Postgis
First install postgresql with the postgis extension; for debian one can use the apt package manager, e.g.
```shell
$ sudo apt install postgresql-12
$ sudo apt install postgresql-12-postgis-3 
$ sudo apt install postgresql-12-postgis-scripts
```
Installation instructions for other package systems may be found on the [postgis website](https://postgis.net/install/)

### Database setup
For Postgis, you'll need to create a postgres user, a database and the postgis extension inside that database:
```shell
$ sudo su - postgres
$ createuser <dbuser> -W <psswd>
$ createdb  <dbname>
$ psql <dbname>
> CREATE EXTENSION postgis;
```
The database user `<dbuser>`, the password `<psswd>` and the database name `<dbname>` should be substituted in the django settings file `project/settings/base.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '<dbname>',
        'USER': '<dbuser>',
        'PASSWORD': '<psswd>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
### Running the service
The configuration above will run the server on the localhost. To start up the server, open a terminal, optionally activate your virtual environment, and then type
```shell
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
$ python manage.py loaddata stats
```
Here the first 2 lines are only necessary the first time, or when the database schema has been updated. The last line is only required at installation.

More details, including for other platforms, see the GeoDjango
installation documentation at
https://docs.djangoproject.com/en/3.0/ref/contrib/gis/install/.

## Docker-compose
There is also a `docker-compose.yml` file that contains a recipe to run the database and web frontend in two separate containers. You will need to download `docker` and `docker-compose` (see [here](https://docs.docker.com/compose/)). After installing these tools, you need to make sure that the host in `project/settings/base.py` is set to `db` and the database user and password match the `POSTGRES_USER` and `POSTGRES_PASSWORD` in the docker compose yaml file, e.g.
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'exeveda',
        'USER': 'dbuser',
        'PASSWORD': 'dbpsswd',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```
Furthermore, one should edit the allowed hosts in the local settings `project/settings/local.py`,
```python
ALLOWED_HOSTS = ['*']
```
Once this configuration is done, starting the database and web frontend is done by
```shell
$ docker-compose build .
$ docker-compose up
$ docker-compose run web python manage.py loaddata stats
```

## Creating an admin user
Run the following command:
```shell
python manage.py createsuperuser
```
and provide the requested user name, email address and password. If you are using the docker images you can do
```shell
$ docker-compose run web python manage.py createsuperuser
```

## Wordpress styling
Styling of the frontend is provided by the C3S wordpress theme, which you need to have access to. If so, the styling can be applied to the web frontend by setting 
```python
WORDPRESS=True
```
in the local settings file `project/settings/local.py` and creating a symbolic link from `exevada/apps/exevada/static/wp-content` to the installed wordpress `wp-content` folder.