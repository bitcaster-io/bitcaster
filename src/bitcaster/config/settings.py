import logging
from collections import OrderedDict
from pathlib import Path

from django.utils.translation import ugettext_lazy as _
from django_regex.utils import RegexList

from bitcaster.config.environ import env

from . import logging_conf  # noqa

logger = logging.getLogger(__name__)

PACKAGE_DIR = Path(__file__).parent.parent  # bitcaster/
BITCASTER_DIR = PACKAGE_DIR  # backward compatibility - needed by plugins
SOURCE_DIR = PACKAGE_DIR.parent  # src/
PROJECT_DIR = SOURCE_DIR.parent
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',

    # Useful template tags:
    'django.contrib.humanize',

    # Useful libraries and add-ons
    'constance.backends.database',
    'reversion',
    'crispy_forms',
    'impersonate',
    'corsheaders',
    'dal',
    'dal_select2',
    'django_sysinfo',
    'admin_extra_urls',
    'rest_framework',
    'constance',
    'django_countries',
    'adminfilters',
    'social_django',
    'django_extensions',
    'django_cleanup.apps.CleanupConfig',
    'django_db_logging',
    'crashlog',
    # 'django_celery_results',

    # Admin
    'django.contrib.admin',
    # 'bitcaster.config.admin.AdminConfig',

    'bitcaster.web',
    'bitcaster.apps.Config',
]

DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',  # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',  # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',  # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',  # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',  # '25 October 2006', '25 October, 2006'
]
DATETIME_FORMAT = '%Y-%m-%d %H:%M'
DATE_FORMAT = '%Y-%m-%d'

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M',     # '2006-10-25 14:30'
    '%Y/%m/%d %H:%M',     # '2006/10/25 14:30'
    '%d %b %Y %H:%M',     # '25 Oct 2006 14:30'
    '%Y %b %d %H:%M',     # '2006 Oct 25 14:30'

    # '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    # '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    # '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    # '%Y-%m-%d',              # '2006-10-25'
    # '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    # '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    # '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    # '%m/%d/%Y',              # '10/25/2006'
    # '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    # '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    # '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    # '%m/%d/%y',              # '10/25/06'
]


# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'bitcaster.middleware.exception.ExceptionHandlerMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'bitcaster.middleware.setup.SetupMiddleware',
    'bitcaster.middleware.env.BitcasterEnvMiddleware',
    'bitcaster.middleware.security.SecurityHeadersMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'bitcaster.middleware.i18n.UserLanguageMiddleware',
    'bitcaster.middleware.timezone.UserTimezoneMiddleware',
    'bitcaster.middleware.message.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

AUTH_USER_MODEL = 'bitcaster.user'
SECRET_KEY = env('SECRET_KEY')
FERNET_KEYS = [SECRET_KEY] + env('FERNET_KEYS')
ON_PREMISE = env('ON_PREMISE')

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_NAME = 'bitcasterid'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
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
    'crashlog': env.db('DATABASE_URL',
                       default='psql://postgres:@127.0.0.1:5432/bitcaster'),
}

DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['crashlog']['ATOMIC_REQUESTS'] = True
DATABASE_ROUTERS = [
    'bitcaster.routers.DBLogRouter',
]
# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = env('TIME_ZONE')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#GUAguage-code
LANGUAGE_CODE = 'en-us'
LANGUAGE_COOKIE_NAME = 'bitcaster-language'
LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
    ('it', _('Italian')),
)
LOCALE_PATHS = (
    str(PACKAGE_DIR / 'LOCALE'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

SILENCED_SYSTEM_CHECKS = ['admin.E404',  # 'django.contrib.messages.context_processors.messages' must be enabled ...
                          'admin.E409',
                          ]
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(PACKAGE_DIR / 'web/templates'),
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
                'bitcaster.web.context_processors.messages',
                'bitcaster.web.context_processors.bitcaster',
                # 'social_django.context_processors.backends',
                # 'social_django.context_processors.login_redirect',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not env.bool('DEBUG', False)

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'bitcaster.config.urls'
URL_PREFIX = env('URL_PREFIX')
SETUP_URL = '/setup/'
USE_X_FORWARDED_HOST = True

# STATIC FILE CONFIGURATION
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = env.str('STATIC_ROOT')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = f'/{URL_PREFIX}static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(BITCASTER_DIR / 'web' / 'static'),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = env.str('MEDIA_ROOT')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = f'/{URL_PREFIX}media/'

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

KEY_FUNCTION = 'bitcaster.utils.cache.make_key'

CACHES = {
    'default': env.cache('REDIS_CACHE_URL'),
    'lock': env.cache('REDIS_LOCK_URL'),
}

TSDB_STORE = env('REDIS_TSDB_URL')
# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'bitcaster.backends.BitcasterBackend',  # only for permissions
    'bitcaster.backends.BitcasterLDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
# Some really nice defaults
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Custom user app defaults
# Select the correct user model
LOGIN_REDIRECT_URL = '/'
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
CELERY_RESULT_BACKEND = env.str('CELERY_BROKER_URL')
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
    'fields_mapping': ['bitcaster.utils.constance.FieldMappingField', {}],
    'ldap_dn': ['bitcaster.utils.constance.LdapDNField', {
        'required': False,
    }],

    # 'log_message': ['django.forms.fields.ChoiceField', {
    #     'widget': 'django.forms.Select',
    #     'choices': ((0, 'None'), (1, 'Template'), (2, 'Arguments'), (3, 'Full message'))
    # }],

    'yes_no_null_select': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': ((None, '-----'), ('yes', 'Yes'), ('no', 'No'))
    }],

    'read_only_text': ['django.forms.fields.CharField', {
        'required': False,
        'widget': 'bitcaster.utils.constance.ObfuscatedInput',
    }],
    'write_only_text': ['django.forms.fields.CharField', {
        'required': False,
        'widget': 'bitcaster.utils.constance.WriteOnlyTextarea',
    }],
    'write_only_input': ['django.forms.fields.CharField', {
        'required': False,
        'widget': 'bitcaster.utils.constance.WriteOnlyInput',
    }],
    'select_group': ['bitcaster.utils.constance.GroupChoiceField', {
        'required': False,
        'widget': 'bitcaster.utils.constance.GroupChoice',
    }],
}

CONSTANCE_CONFIG = OrderedDict({
    # Internal
    'INITIALIZED': (False, '', bool),
    'CONFIGURATION': (0, '', int),
    'SYSTEM_CONFIGURED': (0, '', int),

    # General
    'SITE_URL': ('', '', str),
    'BACKUPS_LOCATION': ('', '', str),
    'ALLOW_CHANGE_PRIMARY_ADDRESS': (False, 'Users can change their primary email address', bool),
    'LOG_NOTIFICATION': (True, 'Enable/Disable notification log', bool),
    'LOG_MESSAGE': (0, 'Log message ', int),
    'LOG_RETENTION_AUDIT': (365, 'Number of days to keep audit log records', int),
    'LOG_RETENTION_EVENTS': (365, 'Number of days to keep events log records', int),
    'LOG_RETENTION_ERRORS': (30, 'Number of days to keep error log rocords', int),
    'SHOW_DISABLED_DISPATCHERS': (True, 'Show dispatcher even if globally disabled', bool),
    'DISPLAY_EXTRA_FIELDS_IN_PROFILE': (True,
                                        'Display custom fields in user profile page', bool),
    # Services
    'RECAPTCHA_PUBLIC_KEY': ('', '', str),
    'RECAPTCHA_PRIVATE_KEY': ('', '', str),
    'GOOGLE_ANALYTICS_CODE': ('', 'Google Analytics code', str),
    'IPSTACK_HOST': ('http://api.ipstack.com/', 'ipstack api addredss', str),
    'IPSTACK_KEY': ('', 'ipstack access key', str),
    # Other
    'ALLOW_REGISTRATION': (False, '', bool),
    'INVITATION_EXPIRE': (60 * 60 * 24, '', int),
    # Email
    'EMAIL_USE_TLS': (False, '', bool),
    'EMAIL_TIMEOUT': (60, '', int),
    'EMAIL_HOST': ('', '', str),
    'EMAIL_HOST_PORT': (0, '', int),
    'EMAIL_HOST_USER': ('', '', str),
    'EMAIL_HOST_PASSWORD': ('', '', str),
    'EMAIL_SENDER': ('noreply@bitcaster.io', '', str),
    'EMAIL_SUBJECT_PREFIX': ('[bitcaster] ', '', str),
    # Ldap
    'AUTH_LDAP_ENABLE': (False, 'Enable LDAP Authentication', bool),
    'AUTH_LDAP_SERVER_URI': ('', 'LDAP server address', str),
    'AUTH_LDAP_BIND_DN': ('', '', 'ldap_dn'),
    'AUTH_LDAP_BIND_PASSWORD': ('', '', str),
    'AUTH_LDAP_BIND_AS_AUTHENTICATING_USER': (False, '', bool),
    'AUTH_LDAP_START_TLS': (False, '', bool),
    'AUTH_LDAP_USER_ATTR_MAP': ('email:mail,name:cn', '', 'fields_mapping'),
    'AUTH_LDAP_USER_QUERY_FIELD': ('email', '', str),

    'AUTH_LDAP_USER_DN_TEMPLATE': ('', 'ie. "uid=%(user)s,ou=users,dc=example,dc=com"', 'ldap_dn'),
    'AUTH_LDAP_ALWAYS_UPDATE_USER': (True, '', bool),
    # 'AUTH_LDAP_AUTHORIZE_ALL_USERS': (False, '', bool),
    # 'AUTH_LDAP_CACHE_TIMEOUT': (0, '', int),
    # 'AUTH_LDAP_USER_SEARCH': ('ou=users,dc=example,dc=com', '', str),
    # 'AUTH_LDAP_CONNECTION_OPTIONS': {},
    # 'AUTH_LDAP_DENY_GROUP': None,
    # 'AUTH_LDAP_FIND_GROUP_PERMS': (False, '', bool),
    # 'AUTH_LDAP_GROUP_SEARCH': None,
    # 'AUTH_LDAP_GROUP_TYPE': None,
    # 'AUTH_LDAP_MIRROR_GROUPS': None,
    # 'AUTH_LDAP_MIRROR_GROUPS_EXCEPT': None,
    # 'AUTH_LDAP_PERMIT_EMPTY_PASSWORD': False,
    # 'AUTH_LDAP_REQUIRE_GROUP': None,
    # 'AUTH_LDAP_USER_QUERY_FIELD': None,
    # 'AUTH_LDAP_USER_ATTRLIST': None,
    # 'AUTH_LDAP_USER_ATTR_MAP': {},
    # 'AUTH_LDAP_USER_FLAGS_BY_GROUP': {},

    # Oauth
    'OAUTH_CALLBACK': ('http://localhost:8000/oauth2callback/', '', str),

    'SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLE_LOGIN': (False, '', bool),
    'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY': ('', '', str),
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': ('', '', str),
    'SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS': ('', 'aaa', str),

    'SOCIAL_AUTH_GITHUB_ORG_ENABLE_LOGIN': (False, '', bool),
    'SOCIAL_AUTH_GITHUB_ORG_KEY': ('', '', str),
    'SOCIAL_AUTH_GITHUB_ORG_SECRET': ('', '', str),
    'SOCIAL_AUTH_GITHUB_ORG_NAME': ('', '', str),

    'SOCIAL_AUTH_GITHUB_ENABLE_LOGIN': (False, '', bool),
    'SOCIAL_AUTH_GITHUB_KEY': ('', '', str),
    'SOCIAL_AUTH_GITHUB_SECRET': ('', '', str),

    'SOCIAL_AUTH_LINKEDIN_OAUTH2_ENABLE_LOGIN': (False, '', bool),
    'SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY': ('', '', str),
    'SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET': ('', '', str),

    'SOCIAL_AUTH_FACEBOOK_ENABLE_LOGIN': (False, '', bool),
    'SOCIAL_AUTH_FACEBOOK_KEY': ('', '', str),
    'SOCIAL_AUTH_FACEBOOK_SECRET': ('', '', str),

    # Hidden
    'LOG_OCCURENCES': (True, 'Enable/Disable event occurences log', bool),
    'LOG_OCCURENCES_RETENTION': (30, 'Occurences log retention days', int),
    'LOG_NOTIFICATION_RETENTION': (30, 'Notification log retention days', int),
    'LOG_ERROR_RETENTION': (30, 'Error log retention days', int),
    'ENABLE_IMPERSONATE': (False, '', bool),
    'ADVANCED_MODE': (False, '', bool),

})
CONSTANCE_CONFIG_FIELDSETS = {'Options': list(CONSTANCE_CONFIG.keys())}

# SENTRY & RAVEN
# need to copy in settings because we inject these values in the templates
SENTRY_ENABLED = env.bool('SENTRY_ENABLED', False)
SENTRY_DSN = env('SENTRY_DSN', '')
if SENTRY_ENABLED:
    import bitcaster

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    def before_send(event, hint):
        try:
            pass
        except Exception:
            pass
        return event

    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()],
                    release=bitcaster.get_full_version(),
                    send_default_pii=True,
                    before_send=before_send,
                    debug=False)

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


SYSINFO = {'host': True,
           'os': True,
           'python': True,
           'modules': True,
           'project': {
               'mail': True,
               'installed_apps': True,
               'databases': True,
               'MEDIA_ROOT': True,
               'STATIC_ROOT': True,
               'CACHES': True
           },
           'checks': None,
           'extra': {'plugins': get_plugins}
           }

# SOCIAL-AUTH
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['key', 'invitation']
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    # 'social_core.backends.github.GithubOAuth2',
    # 'social_core.backends.github.GithubOrganizationOAuth2',
    'bitcaster.social_auth.BitcasterGithubOrganizationOAuth2',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
)

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',  # 0

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',  # 1

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',  # 2

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',  # 3

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',  # 4

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',  # 4

    # 'bitcaster.social_auth.associate_by_email',  # 5
    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',  # 6  create SocialAuth instance

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',  # 7

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',  # 8
    'bitcaster.social_auth.associate_invitation',  # 9
    'bitcaster.social_auth.link_social_account',  # 10
)

SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login/'
SOCIAL_AUTH_LOGIN_URL = '/login/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/'
SOCIAL_AUTH_INACTIVE_USER_URL = '/'
SOCIAL_AUTH_USER_MODEL = 'bitcaster.User'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + SOCIAL_AUTH_AUTHENTICATION_BACKENDS
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'name', ]
SOCIAL_AUTH_STRATEGY = 'bitcaster.social_auth.BitcasterStrategy'

SOCIAL_AUTH_GOOGLE_OAUTH2_LOGIN_URL = '/'

SOCIAL_AUTH_GOOGLE_PLUS_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline'
}

SOCIAL_AUTH_LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress', 'r_liteprofile']
SOCIAL_AUTH_LINKEDIN_FIELD_SELECTORS = ['email-address', 'headline', 'industry']
SOCIAL_AUTH_LINKEDIN_EXTRA_DATA = [('id', 'id'),
                                   ('firstName', 'first_name'),
                                   ('lastName', 'last_name'),
                                   ('emailAddress', 'email_address'),
                                   ('headline', 'headline'),
                                   ('industry', 'industry')]

# DJANGO-RECAPTCHA
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
# os.environ['RECAPTCHA_DISABLE'] = 'True'

# DJANGO-REGISTRATION
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window; you may, of course, use a different value.

OTP_KEY = 'A' * 32
CONFIRM_EMAIL_EXPIRE = 60 * 60 * 24  # 1 day

if DEBUG:
    ignored = RegexList((SETUP_URL, '/tpl/.*', '/api/.*', '/dal/.*'))

    def show_ddt(request):
        if request.user.is_authenticated:
            if request.path in ignored:
                return False
        return 'HTTP_X_DDT' in request.META

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
    MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': show_ddt,
                            'JQUERY_URL': '',
                            }
    DEBUG_TOOLBAR_PANELS = [
        'bitcaster.utils.ddt.UserInfoPanel',
        # 'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        # 'debug_toolbar.panels.settings.SettingsPanel',
        # 'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        # 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        # 'debug_toolbar.panels.signals.SignalsPanel',
        # 'debug_toolbar.panels.logging.LoggingPanel',
        # 'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
    INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0', '*']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1',
    'http://localhost'
)
# CORS_URLS_REGEX = rf'{STATIC_URL}.*$'
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_METHODS = (
    # 'DELETE',
    'GET',
    'OPTIONS',
    # 'PATCH',
    'POST',
    # 'PUT',
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

IMPERSONATE = {
    'PAGINATE_COUNT': 50,
    'REQUIRE_SUPERUSER': True,
    # 'REDIRECT_URL': 'me/',
    'CUSTOM_USER_QUERYSET': 'bitcaster.utils.impersonate.queryset'
}
