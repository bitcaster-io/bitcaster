import logging
from pathlib import Path
from urllib.parse import urlparse

from . import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
SETTINGS_DIR = Path(__file__).parent  # .../src/bitcaster/config
PROJECT_ROOT = SETTINGS_DIR.parent.parent.parent  # .../src/bitcaster/
SOURCE_DIR = PROJECT_ROOT / "src"  # .../src
PACKAGE_DIR = SOURCE_DIR / "bitcaster"  # .../src/bitcaster/
LOCALE_PATHS = [str((PACKAGE_DIR / "LOCALE").absolute())]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
SECRET_KEY = env("SECRET_KEY")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
SECURE_PROXY_SSL_HEADER = env.list("SECURE_PROXY_SSL_HEADER")
USE_X_FORWARDED_HOST = env("USE_X_FORWARDED_HOST")
USE_X_FORWARDED_PORT = env("USE_X_FORWARDED_PORT")

DEBUG = env.bool("DEBUG")
INTERNAL_IPS = env.list("INTERNAL_IPS")
ALLOWED_HOSTS: list[str] = env("ALLOWED_HOSTS")

# Application definition

INSTALLED_APPS = [
    "bitcaster.web.apps.Config",
    "bitcaster.web.theme.apps.Config",
    "bitcaster.webpush.apps.Config",
    "bitcaster.social.apps.Config",
    "unfold.apps.BasicAppConfig",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "unfold.contrib.location_field",  # optional, if django-location-field package is used
    "unfold.contrib.constance",  # optional, if django-constance package is used
    # "django.contrib.admin",
    "bitcaster.admin_site.BitcasterAdminConfig",
    # "bitcaster.chrome.apps.Config",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django_select2",
    "adminactions",
    "admin_extra_buttons",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.gitlab",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.linkedin_oauth2",
    "allauth.socialaccount.providers.openid_connect",
    "allauth.socialaccount.providers.twitter",
    "csp",
    "smart_selects",
    "adminfilters",
    "debug_toolbar",
    # -- start editors
    "jsoneditor",
    "django_svelte_jsoneditor",
    "django_ace",
    "tinymce",
    # -- end editors
    "reversion",
    "taggit",
    # "treebeard",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "flags",
    "constance",
    "constance.backends.database",
    "anymail",
    "bitcaster.apps.Config",
    "bitcaster.console.apps.Config",
    "bitcaster.help.apps.Config",
    "bitcaster.pwa.apps.Config",
    "tailwind",
    "issues",
    *env("EXTRA_APPS"),
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "bitcaster.middleware.cors.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "bitcaster.middleware.errors.ExceptionHandlingMiddleware",
    "csp.middleware.CSPMiddleware",
    "bitcaster.middleware.user_agent.UserAgentMiddleware",
    "bitcaster.middleware.state.StateMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/"

ROOT_URLCONF = "bitcaster.config.urls"
SILENCED_SYSTEM_CHECKS = [
    "security.W019",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bitcaster.social.context_processors.available_providers",
                "bitcaster.web.context_processors.version",
                "bitcaster.web.context_processors.debug",
            ],
        },
    },
]

WSGI_APPLICATION = "bitcaster.config.wsgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("CHANNEL_SERVER")],
        },
    },
}

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
CSRF_COOKIE_SAMESITE = "Strict"

DATABASES = {
    "default": env.db(),
}

CACHE_URL = env("CACHE_URL")
REDIS_URL = urlparse(CACHE_URL).hostname
CACHES = {
    "default": env.cache(),
    "select2": env.cache(),
}
CACHES["default"]["KEY_PREFIX"] = env("ENVIRONMENT")
CACHES["select2"]["KEY_PREFIX"] = env("ENVIRONMENT")

AUTH_USER_MODEL = "bitcaster.user"

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

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

AUTHENTICATION_BACKENDS = [
    "bitcaster.auth.backends.BitcasterBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
ugettext = lambda s: s  # noqa
LANGUAGE_COOKIE_NAME = "language"
LANGUAGES = (
    ("en", "English"),
    ("es", "Español"),
    ("it", "Italiano"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("ar", "العربية"),
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

SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
SESSION_COOKIE_PATH = env("SESSION_COOKIE_PATH")
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN")
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

X_FRAME_OPTIONS = "SAMEORIGIN"

STORAGES = {
    "default": env.storage("STORAGE_DEFAULT"),
    "staticfiles": env.storage("STORAGE_STATIC"),
    "mediafiles": env.storage("STORAGE_MEDIA") or env.storage("STORAGE_DEFAULT"),
}

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

DATE_FORMATS = [
    "%m-%d-%Y",  # 12-31-2000
    "%d %B %Y",  # 1 February 2025
    "%d %b %Y",  # 1 Feb 2025
    "%B %d, %Y",  # February 1, 2025
    "%b %d, %Y",  # Feb 1, 2025
    "%Y-%m-%d",  # 2000-12-31
    "%d-%m-%Y",  # 31-12-2000
    "%a, %d %B %Y",  # Mon, 1 February 2025
    "%a, %d %b %Y",  # Mon, 1 Feb 2025
]

TIME_FORMATS = [
    "%H:%M",
    "%H:%M %Z",
    "%I:%M%p %Z",
    "%I:%M%p",
]

logger = logging.getLogger(__name__)

from .fragments.agents import *  # noqa
from .fragments.api import *  # noqa
from .fragments.bitcaster import *  # noqa
from .fragments.constance import *  # noqa
from .fragments.cors import *  # noqa
from .fragments.csp import *  # noqa
from .fragments.debug_toolbar import *  # noqa
from .fragments.dramatiq import *  # noqa
from .fragments.flags import *  # noqa
from .fragments.help import *  # noqa
from .fragments.logging import *  # noqa
from .fragments.pwa import *  # noqa
from .fragments.rest_framework import *  # noqa
from .fragments.sentry import *  # noqa
from .fragments.social_auth import *  # noqa
from .fragments.tailwind import *  # noqa
from .fragments.tinymce import *  # noqa
from .fragments.unfold import *  # noqa
from .fragments.json_editor import *  # noqa
