"""
Django settings for djangostock project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import dj_database_url
from decouple import Csv, config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================================================================
# CORE SETTINGS
# ==============================================================================
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure$djangostock.settings.local")

API_KEY_TWELVEDATA = config("API_KEY_TWELVEDATA")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

AUTH_USER_MODEL = "application.User"

# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djangostock.application.application.ApplicationConfig",
    "rest_framework",
    "rest_framework_simplejwt",
    "celery",
    "django_celery_beat",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "djangostock.urls"

INTERNAL_IPS = ["127.0.0.1"]

# WSGI_APPLICATION = "djangostock.wsgi.application"
ASGI_APPLICATION = "djangostock.asgi.application"

# ==============================================================================
# MIDDLEWARE SETTINGS
# ==============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==============================================================================
# TEMPLATES SETTINGS
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "djangostock/templates"],
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
# ==============================================================================
# REST SETTINGS
# ==============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# ==============================================================================
# SIMPLE JWT SETTINGS
# ==============================================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "SIGNING_KEY": SECRET_KEY,
}

# ==============================================================================
# DATABASES SETTINGS
# ==============================================================================
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
    )
}


# ==============================================================================
# AUTHENTICATION AND AUTHORIZATION SETTINGS
# ==============================================================================
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# ==============================================================================
# CELERY SETTINGS
# ==============================================================================
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379")
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="pyamqp://127.0.0.1:5672")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# ==============================================================================
# I18N AND L10N SETTINGS
# ==============================================================================
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")

TIME_ZONE = config("TIME_ZONE", default="UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]


# ==============================================================================
# STATIC FILES SETTINGS
# ==============================================================================
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR.parent.parent / "static"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# ==============================================================================
# MEDIA FILES SETTINGS
# ==============================================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR.parent.parent / "media"


# ==============================================================================
# THIRD-PARTY SETTINGS
# ==============================================================================


# ==============================================================================
# FIRST-PARTY SETTINGS
# ==============================================================================

DJANGOSTOCK_ENVIRONMENT = config("DJANGOSTOCK_ENVIRONMENT", default="local")
