import logging
from collections import OrderedDict
from pathlib import Path

from django.utils.translation import ugettext_lazy as _
from django_regex.utils import RegexList

from bitcaster.config.environ import env

from .logging_conf import LOGGING

logger = logging.getLogger(__name__)

BITCASTER_DIR = Path(__file__).parent.parent.parent  # (bitcaster/config/settings/base.py - 3 = bitcaster/)
SOURCE_DIR = BITCASTER_DIR.parent  # (bitcaster/config/settings/base.py - 3 = bitcaster/)
PROJECT_DIR = SOURCE_DIR.parent
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    'django.contrib.humanize',

    # Useful libraries and add-ons
    'constance.backends.database',
    'snowpenguin.django.recaptcha2',
    'crispy_forms',
    'jsoneditor',
    'django_sysinfo',
    'admin_extra_urls',
    'rest_framework',
    'constance',
    'django_countries',
    'adminfilters',
    'social_django',
    'django_extensions',

    # 'django_celery_beat',
    # 'django_celery_results',

    # Admin
    'django.contrib.admin',

    'bitcaster.apps.Config',
]

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'bitcaster.middleware.setup.SetupMiddleware',
    'bitcaster.middleware.env.BitcasterEnvMiddleware',
    'bitcaster.middleware.security.SecurityHeadersMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'bitcaster.middleware.logger.LoggerMiddleware',
]

AUTH_USER_MODEL = 'bitcaster.user'
SECRET_KEY = env('SECRET_KEY')
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_NAME = "bitcasterid"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"
# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DEBUG', False)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_SUBJECT_PREFIX = '[Bitcaster]'
# EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
# EMAIL_HOST = env.str('EMAIL_HOST')
# EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = env('EMAIL_PORT')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [

]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Uses django-environ to accept uri format
# See: https://django-environ.readthedocs.io/en/latest/#supported-types
DATABASES = {
    'default': env.db('DATABASE_URL',
                      default='psql://postgres:@127.0.0.1:5432/bitcaster'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Rome'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#GUAguage-code
LANGUAGE_CODE = 'en-us'
LANGUAGE_COOKIE_NAME = 'bitcaster-language'
LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
)
LOCALE_PATHS = (
    str(BITCASTER_DIR / 'locale'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
TEMPLATES_DIR = [
    str(BITCASTER_DIR / 'templates'),

]
# TEMPLATE_DEMO CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(BITCASTER_DIR / 'templates'),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'bitcaster.context_processors.bitcaster',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not env.bool('DEBUG', False)

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = env.str('STATIC_ROOT', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    # '/data/PROGETTI/saxix/mercury/src/bitcaster/static',
    # str(PROJECT_DIR / 'static'),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = env.str('MEDIA_ROOT', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'bitcaster.config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'bitcaster.config.wsgi.application'

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    # 'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'KEY_PREFIX': 'bitcaster',
        'LOCATION': env('REDIS_CACHE_URL'),
        # "LOCATION": "redis://127.0.0.1:6379/1",

        'OPTIONS': {
            'PICKLE_VERSION': -1,  # default
            # 'PARSER_CLASS': 'redis.connection.HiredisParser',
            # 'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            "CLIENT_CLASS": "django_redis.client.DefaultClient"

        },
    },
    'lock': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'KEY_PREFIX': 'bitcaster-lock',
        'LOCATION': env('REDIS_LOCK_URL'),
        'OPTIONS': {
            'PICKLE_VERSION': -1,  # default
            # 'PARSER_CLASS': 'redis.connection.HiredisParser',
            # 'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            "CLIENT_CLASS": "django_redis.client.DefaultClient"

        },
    },
}

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'bitcaster.backends.BitcasterBackend',
    'django.contrib.auth.backends.ModelBackend',
)
# Some really nice defaults
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Custom user app defaults
# Select the correct user model
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'login'

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# BITCASTER
PLUGINS_AUTOLOAD = env.bool('PLUGINS_AUTOLOAD', True)

# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

JSON_EDITOR_JS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.js'
JSON_EDITOR_CSS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.css'

# REST_FRAMEWORK

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'bitcaster.api.permissions.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'bitcaster.permissions.IsAuthenticated',
        # 'rest_framework.permissions.AllowAny',
        # 'bitcaster.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_THROTTLE_CLASSES': (

    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# CELERY SETTINGS
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', False)
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_LOG_FILE = None
CELERY_REDIRECT_STDOUTS = True

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# CONSTANCE
# CONSTANCE_REDIS_CONNECTION = env('REDIS_CONSTANCE_URL')
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_ADDITIONAL_FIELDS = {
    'yes_no_null_select': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': ((None, "-----"), ("yes", "Yes"), ("no", "No"))
    }],
    # 'yes_no_null_select': ['django.forms.fields.ChoiceField', {
    #     'widget': 'django.forms.Select',
    #     'choices': ((None, "-----"), ("yes", "Yes"), ("no", "No"))
    # }],
}

CONSTANCE_CONFIG = OrderedDict({
    'INITIALIZED': (False, '', bool),
    'SYSTEM_CONFIGURED': (False, '', bool),
    'SITE_URL': ('', '', str),
    'RECAPTCHA_PUBLIC_KEY': ('', '', str),
    'RECAPTCHA_PRIVATE_KEY': ('', '', str),
    'ENABLE_SENTRY': ('', '', str),
    'SENTRY_DSN': ('', '', str),
    'HOSTIP_ADDRESS': ('http://api.hostip.info/get_html.php',
                       'api.hostip.info info',
                       str),
    'OAUTH_CALLBACK': ('http://localhost:8000/oauth2callback/', '', str),
    'ALLOW_REGISTRATION': (False, '', bool),
    'ON_PREMISE': (True, '', bool),
    'INVITATION_EXPIRE': (60 * 60 * 24, '', int),
    'EMAIL_USE_TLS': (False, '', bool),
    'EMAIL_TIMEOUT': (60, '', int),
    'EMAIL_HOST': ('', '', str),
    'EMAIL_HOST_PORT': (0, '', int),
    'EMAIL_HOST_USER': ('', '', str),
    'EMAIL_HOST_PASSWORD': ('', '', str),
    'EMAIL_SENDER': ('bitcaster@noreply.org', '', str),
    'EMAIL_SUBJECT_PREFIX': ('[bitcaster] ', '', str),
    'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY': ('', '', str),
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': ('', '', str),
    'SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY': ('', '', str),
    'SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET': ('', '', str),
    'SOCIAL_AUTH_GITHUB_KEY': ('', '', str),
    'SOCIAL_AUTH_GITHUB_SECRET': ('', '', str),
    'SOCIAL_AUTH_FACEBOOK_KEY': ('', '', str),
    'SOCIAL_AUTH_FACEBOOK_SECRET': ('', '', str),

})
CONSTANCE_CONFIG_FIELDSETS = {"Options": list(CONSTANCE_CONFIG.keys())}

# SENTRY & RAVEN
if env.bool('ENABLE_SENTRY', False):
    import raven
    import bitcaster.state

    LOGGING['handlers']['sentry'] = {'level': 'ERROR',
                                     # 'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                                     'class': 'bitcaster.logging.BitcasterHandler',
                                     'extra': {'state': bitcaster.state.state},
                                     }

    INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]
    RAVEN_CONFIG = {
        'dsn': env('SENTRY_DSN'),
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        'release': raven.fetch_git_sha(str(PROJECT_DIR)),
    }
    # We recommend putting this as high in the chain as possible
    MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
                  ] + list(MIDDLEWARE)

# OAUTH2
GOOGLE_APP_ID = env.str('GOOGLE_APP_ID', '')
GOOGLE_APP_SECRET = env.str('GOOGLE_APP_SECRET', '')

SLACK_APP_ID = env.str('SLACK_APP_ID', '')
SLACK_APP_SECRET = env.str('SLACK_APP_SECRET', '')

TWITTER_APP_ID = env.str('TWITTER_APP_ID', '')
TWITTER_APP_SECRET = env.str('TWITTER_APP_SECRET', '')


# SYSINFO

def get_plugins(x):
    from bitcaster.dispatchers.registry import dispatcher_registry
    return dispatcher_registry.as_choices()


SYSINFO = {"host": True,
           "os": True,
           "python": True,
           "modules": True,
           "project": {
               "mail": True,
               "installed_apps": True,
               "databases": True,
               "MEDIA_ROOT": True,
               "STATIC_ROOT": True,
               "CACHES": True
           },
           "checks": None,
           "extra": {'plugins': get_plugins}
           }

# SOCIAL-AUTH
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['key', 'invitation']
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
)
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    # 'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'bitcaster.social_auth.associate',
    'bitcaster.social_auth.avatar',
    # 'social_core.pipeline.user.create_user',
    'bitcaster.social_auth.associate_invitation',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    # 'social_core.pipeline.debug.debug',

)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/me/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
SOCIAL_AUTH_LOGIN_URL = '/login-url/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-user/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
SOCIAL_AUTH_INACTIVE_USER_URL = '/inactive-user/'
SOCIAL_AUTH_USER_MODEL = 'bitcaster.User'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + SOCIAL_AUTH_AUTHENTICATION_BACKENDS
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'name', ]
SOCIAL_AUTH_STRATEGY = 'bitcaster.social_auth.BitcasterStrategy'

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
# SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/userinfo.email',
#                                    'https://www.googleapis.com/auth/userinfo.profile',
#                                    ]
SOCIAL_AUTH_GOOGLE_PLUS_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline'
}

#
# # SOCIAL_AUTH_GITHUB_ORG_NAME = 'bitcaster-io'
# SOCIAL_AUTH_GITHUB_KEY = env('SOCIAL_AUTH_GITHUB_KEY')
# SOCIAL_AUTH_GITHUB_SECRET = env('SOCIAL_AUTH_GITHUB_SECRET')
#
# # SOCIAL_AUTH_GITHUB_KEY = env('SOCIAL_AUTH_GITHUB_KEY')
# # SOCIAL_AUTH_GITHUB_SECRET = env('SOCIAL_AUTH_GITHUB_SECRET')
#
# DJANGO-RECAPTCHA
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
# os.environ['RECAPTCHA_DISABLE'] = 'True'

# DJANGO-REGISTRATION
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window; you may, of course, use a different value.

OTP_KEY = 'A' * 32
CONFIRM_EMAIL_EXPIRE = 60 * 60 * 24  # 1 day

# DEBUG-TOOLBAR
if False:
    ignored = RegexList(('/setup/', '/tpl/.*'))

    def show_ddt(request):
        if request.user.is_authenticated:
            if request.path in ignored:
                return False
        return True

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
    MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': show_ddt,
                            'JQUERY_URL': ''}
    INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0', '*']
