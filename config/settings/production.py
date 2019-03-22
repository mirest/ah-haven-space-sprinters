import dj_database_url
import django_heroku

from config.settings.default import *

DEBUG = False

ALLOWED_HOSTS += ['.herokuapp.com']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

django_heroku.settings(locals(), test_runner=False)

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')

EMAIL_HOST = os.environ.get('EMAIL_HOST')

EMAIL_PORT = 587

DATABASES = {
    'default': {}
}

DATABASES['default'] = dj_database_url.config(default=os.environ.get("DATABASE_URL", None))

MIDDLEWARE += ('whitenoise.middleware.WhiteNoiseMiddleware',)

INSTALLED_APPS += ['storages']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
