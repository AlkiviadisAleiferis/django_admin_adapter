import os
import sys
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

MEDIA_URL = "/media/"
STATIC_URL = backend_settings.STATIC_URL

CACHES = backend_settings.CACHES
SESSION_ENGINE = backend_settings.SESSION_ENGINE
SESSION_CACHE_ALIAS = backend_settings.SESSION_CACHE_ALIAS

if DEBUG:
    import socket

    # DJANGO DEBUG TOOLBAR
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1",
        "http://localhost",
    ]

    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        os.environ["DB_IP"],
        os.environ["REDIS_IP"],
        os.environ["ADMIN_IP"],
        "10.0.2.2",
    ]
else:
    CSRF_TRUSTED_ORIGINS = os.environ["ADMIN_CSRF_TRUSTED_ORIGINS"].split()
    ALLOWED_HOSTS = [
        os.environ["DB_IP"],
        os.environ["REDIS_IP"],
        os.environ["ADMIN_IP"],
    ] + os.environ["ADMIN_ALLOWED_HOSTS"].split()
    INTERNAL_IPS = [
        os.environ["DB_IP"],
        os.environ["REDIS_IP"],
        os.environ["ADMIN_IP"],
    ]

INSTALLED_APPS.extend(
    [
        "cacheops",
        "django.forms",
        "django_jsonform",
        "rest_framework",
        "admin_auto_filters",
        "admin.django_admin",
    ]
)

ROOT_URLCONF = "admin.django_admin.urls"
WSGI_APPLICATION = "wsgi.application"

STATICFILES_DIRS = (str(BASE_DIR / "admin" / "django_admin" / "static"),)

STATIC_ROOT = str(os.environ["ADMIN_STATIC_ROOT"])
MEDIA_ROOT = str(os.environ["ADMIN_MEDIA_ROOT"])


# % ------------------ STORAGES ----------------------------

LOCAL_STORAGE = {  # local
    "BACKEND": "django.core.files.storage.FileSystemStorage",
    "OPTIONS": {
        "location": MEDIA_ROOT,
        "base_url": MEDIA_URL,
    },
}

STORAGES = {
    "default": LOCAL_STORAGE,
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# % ------------------ TEMPLATES ----------------------------
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

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
