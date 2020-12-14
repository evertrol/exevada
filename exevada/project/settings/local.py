import os
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", default="foo")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=1))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", default="localhost").split(" ")

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

WORDPRESS = True

LOCKDOWN_ENABLED = (os.get("LOCKDOWN_ENABLED", "false").lower() in ["true", "1"])

LOCKDOWN_PASSWORDS = (os.get("LOCKDOWN_PASSWORD", "letmein"),)
