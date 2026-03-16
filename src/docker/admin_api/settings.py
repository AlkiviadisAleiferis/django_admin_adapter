import os
import sys
from datetime import timedelta
from pathlib import Path

from backend import settings as backend_settings

BASE_DIR = Path(__file__).resolve().parent  # PROJECT_NAME dir in /opt in container
sys.path.append(BASE_DIR)


SECRET_KEY = "1234"


# % ------------------ import backend settings ------------------
DEBUG = backend_settings.DEBUG

AUTH_USER_MODEL = backend_settings.AUTH_USER_MODEL
INSTALLED_APPS = backend_settings.INSTALLED_APPS
MIDDLEWARE = backend_settings.MIDDLEWARE
DATABASES = backend_settings.DATABASES

AUTH_PASSWORD_VALIDATORS = backend_settings.AUTH_PASSWORD_VALIDATORS

USE_TZ = backend_settings.USE_TZ
TIME_FORMAT = backend_settings.TIME_FORMAT
DATETIME_FORMAT = backend_settings.DATETIME_FORMAT
DATE_FORMAT = backend_settings.DATE_FORMAT

LANGUAGE_CODE = backend_settings.LANGUAGE_CODE
TIME_ZONE = backend_settings.TIME_ZONE
USE_I18N = backend_settings.USE_I18N
DEFAULT_AUTO_FIELD = backend_settings.DEFAULT_AUTO_FIELD

MEDIA_URL = backend_settings.MEDIA_URL
STATIC_URL = backend_settings.STATIC_URL

CACHES = backend_settings.CACHES
SESSION_ENGINE = backend_settings.SESSION_ENGINE
SESSION_CACHE_ALIAS = backend_settings.SESSION_CACHE_ALIAS

CORS_ALLOWED_ORIGINS = os.environ["ADMIN_API_CORS_ALLOWED_ORIGINS"].split()

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
]

INTERNAL_IPS = [
    os.environ["DB_IP"],
    os.environ["REDIS_IP"],
    os.environ["ADMIN_API_IP"],
    "10.0.2.2",
]

MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")

INSTALLED_APPS.extend(
    [
        "silk",
        "cacheops",
        "rest_framework",
        "admin_api",
        "corsheaders",
    ]
)

ROOT_URLCONF = "admin_api.urls"
WSGI_APPLICATION = "wsgi.application"

STATICFILES_DIRS = (str(BASE_DIR / "admin_api" / "static"),)

STATIC_ROOT = str(os.environ["ADMIN_API_STATIC_ROOT"])
MEDIA_ROOT = str(os.environ["ADMIN_API_MEDIA_ROOT"])

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
            "base_url": MEDIA_URL,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=1200),
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=3600 * 3),
}

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%d/%m/%Y - %H:%M",
    "DATE_FORMAT": "%d/%m/%Y",
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '1000/hour',  # Rate for AdminAnonRateThrottle
    #     'user': '1000/hour',  # Rate for AdminUserRateThrottle
    # },
}
