# Install Guide

## Linux system-wide
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
$ createuser <db usr> -W <psswd>
$ createdb  <db name>
$ psql <db name>
> CREATE EXTENSION postgis;
```
The database user `<db_usr>`, the password `<psswd>` and the database name `<db_name>` should be noted for later usage.
Many more details, including for other platforms, see the GeoDjango
installation documentation at
https://docs.djangoproject.com/en/3.0/ref/contrib/gis/install/ .



### Python dependencies
We have included a set of required python-3 packages in `requirements.txt`. You can optionally create a virtual environment to contain them, and run
```shell
pip install -r requirements.txt
```


## Anaconda
In case you prefer Conda, you can set up a new environment as follows:

        conda create -n exevada django libspatialite python=3.8

for the SQLite variant, and

        conda create -n exevada -c conda-forge  django postgis psycopg2 python=3.8

for the PostgreSQL variant.


## Docker-compose
There is also a `exevada/Dockerfile` file that can be used, either as a
guide line for the installation, or for building the Dockerfile
instead. From the base directory:

        docker build docker
