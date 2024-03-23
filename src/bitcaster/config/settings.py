from pathlib import Path
from typing import List
from urllib.parse import urlparse

from . import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
SETTINGS_DIR = Path(__file__).parent  # .../src/bitcaster/config
PACKAGE_DIR = SETTINGS_DIR.parent  # .../src/bitcaster/
SOURCE_DIR = PACKAGE_DIR.parent.parent  # .../src


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
SECRET_KEY = env("SECRET_KEY")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS: List[str] = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "adminactions",
    "admin_extra_buttons",
    "social_django",
    "csp",
    "django_celery_beat",
    "adminfilters",
    #
    "celery",
    "treebeard",
    "rest_framework",
    "flags",
    "constance",
    #
    "bitcaster.apps.Config",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "csp.middleware.CSPMiddleware",
    "bitcaster.middleware.user_agent.UserAgentMiddleware",
    "bitcaster.middleware.state.StateMiddleware",
    "bitcaster.middleware.minify.HtmlMinMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bitcaster.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "bitcaster.config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

CACHE_URL = env("CACHE_URL")
REDIS_URL = urlparse(CACHE_URL).hostname
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CACHE_URL,
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CACHE_URL,
    },
}

AUTH_USER_MODEL = "bitcaster.user"


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
ugettext = lambda s: s  # noqa
LANGUAGES = (
    ("es", ugettext("Spanish")),  # type: ignore[no-untyped-call]
    ("fr", ugettext("French")),  # type: ignore[no-untyped-call]
    ("en", ugettext("English")),  # type: ignore[no-untyped-call]
    ("ar", ugettext("Arabic")),  # type: ignore[no-untyped-call]
    # ("pt", ugettext("Portuguese")),  # type: ignore[no-untyped-call]
)

TIME_ZONE = env("TIME_ZONE")

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = env("MEDIA_ROOT")
MEDIA_URL = env("MEDIA_URL")
STATIC_ROOT = env("STATIC_ROOT")
STATIC_URL = env("STATIC_URL")
STATICFILES_DIRS: List[str] = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
SESSION_COOKIE_PATH = env("SESSION_COOKIE_PATH")
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN")
# SESSION_COOKIE_HTTPONLY = env("SESSION_COOKIE_HTTPONLY")
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
# SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": "INFO"},
    },
    "root": {
        "handlers": ["console"],
        "level": env("LOGGING_LEVEL"),
    },
}

from .fragments import celery  # noqa
from .fragments import constance  # noqa
from .fragments import rest_framework  # noqa
from .fragments import sentry  # noqa
from .fragments import social_auth  # noqa
