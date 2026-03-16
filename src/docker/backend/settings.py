import os

DEBUG = True if os.environ["DEBUG"] == "true" else False

AUTH_USER_MODEL = "organization.User"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["DB_IP"],
        "PORT": os.environ["DB_PORT"],
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # NOTE: APP order and APP.models definition order
    # inside models.py file
    # affect the contenttypes pks
    "backend.organization.apps.AdministrationConfig",
    "backend.common",
    "backend.real_estate",
    "backend.archive",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

USE_TZ = True
LANGUAGE_CODE = "en-gb"
TIME_FORMAT = "H:i:s"
DATETIME_FORMAT = "Y-m-j - H:i:s"
DATE_FORMAT = "Y-m-j"

TIME_ZONE = "Europe/Athens"
USE_I18N = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# % ------------------ MEDIA/STATIC ----------------------------
MEDIA_URL = "media/"
STATIC_URL = "static/"


# % ------------------ CACHING ----------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}@{}:{}".format(
            os.environ["REDIS_USER"],
            os.environ["REDIS_PASSWORD"],
            os.environ["REDIS_IP"],
            os.environ["REDIS_PORT"],
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.environ["REDIS_PASSWORD"],
        },
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"  # Use the 'default' cache alias defined earlier
