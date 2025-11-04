from pathlib import Path
from urllib.parse import urlparse

from . import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
SETTINGS_DIR = Path(__file__).parent  # .../src/bitcaster/config
PACKAGE_DIR = SETTINGS_DIR.parent  # .../src/bitcaster/
SOURCE_DIR = PACKAGE_DIR.parent.parent  # .../src
LOCALE_PATHS = [str((PACKAGE_DIR / "LOCALE").absolute())]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
SECRET_KEY = env("SECRET_KEY")
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS: list[str] = env("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "bitcaster.web.apps.Config",
    "bitcaster.webpush.apps.Config",
    "bitcaster.social",
    "bitcaster.admin_site.BitcasterAdminConfig",
    # "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_select2",
    "adminactions",
    "admin_extra_buttons",
    "social_django",
    "csp",
    "django_celery_beat",
    "adminfilters",
    "debug_toolbar",
    "django_svelte_jsoneditor",
    "tinymce",
    "reversion",
    "taggit",
    "celery",
    # "treebeard",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "flags",
    "constance",
    "constance.backends.database",
    "anymail",
    "bitcaster.apps.Config",
    *env("EXTRA_APPS"),
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "csp.middleware.CSPMiddleware",
    "bitcaster.middleware.user_agent.UserAgentMiddleware",
    "bitcaster.middleware.state.StateMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
LOGIN_URL = "/login/"
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "bitcaster.social.context_processors.available_providers",
                "bitcaster.web.context_processors.version",
            ],
        },
    },
]

WSGI_APPLICATION = "bitcaster.config.wsgi.application"

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
    # social
    "social_core.backends.azuread.AzureADOAuth2",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.gitlab.GitLabOAuth2",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.linkedin.LinkedinOAuth2",
    "social_core.backends.twitter.TwitterOAuth",
    "bitcaster.social.backend.wso2.Wso2OAuth2",
    "social_core.backends.keycloak.KeycloakOAuth2",
    # local
    "bitcaster.auth.backends.BitcasterBackend",
    # "django.contrib.auth.backends.ModelBackend",
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
X_FRAME_OPTIONS = "SAMEORIGIN"

STORAGES = {
    "default": env.storage("STORAGE_DEFAULT"),
    "staticfiles": env.storage("STORAGE_STATIC"),
    "mediafiles": env.storage("STORAGE_MEDIA") or env.storage("STORAGE_DEFAULT"),
}


from .fragments.agents import *  # noqa
from .fragments.celery import *  # noqa
from .fragments.constance import *  # noqa
from .fragments.csp import *  # noqa
from .fragments.debug_toolbar import *  # noqa
from .fragments.flags import *  # noqa
from .fragments.logging import *  # noqa
from .fragments.rest_framework import *  # noqa
from .fragments.root import *  # noqa
from .fragments.sentry import *  # noqa
from .fragments.social_auth import *  # noqa
from .fragments.tinymce import *  # noqa
