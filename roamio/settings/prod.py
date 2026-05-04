import os
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(f'Missing required environment variable: {name}')
    return value


DEBUG = False

SECRET_KEY = require_env('SECRET_KEY')

ALLOWED_HOSTS = [
    host.strip()
    for host in require_env('ALLOWED_HOSTS').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': require_env('DB_NAME'),
        'USER': require_env('DB_USER'),
        'PASSWORD': require_env('DB_PASSWORD'),
        'HOST': require_env('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
