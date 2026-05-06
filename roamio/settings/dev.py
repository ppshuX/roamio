import os

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'roamio.cn',
    'www.roamio.cn',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'https://roamio.cn',
    'https://www.roamio.cn',
]

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# GitHub Actions runners do not provide Redis unless you add a service container.
# JWT / auth flows and several viewsets touch the default cache; without this,
# django_redis raises connection errors and backend CI fails while the frontend job passes.
if os.environ.get('GITHUB_ACTIONS') == 'true':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'roamio-github-actions',
        }
    }

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
