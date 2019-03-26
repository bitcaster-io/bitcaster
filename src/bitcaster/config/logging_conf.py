import os

level = os.environ.get('BITCASTER_LOG_LEVEL', 'ERROR').upper()

LOGGING = {
    'default_level': 'INFO',
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s '
                      '%(lineno)d %(message)s'
        },
        'short': {
            'format': '%(levelname)-10s %(name)s '
                      ':%(lineno)d '
                      '%(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'INFO',  # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'logging.NullHandler',
            # 'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            # 'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            # 'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'formatter': 'short'
        },
        'db': {
            'level': 'ERROR',
            'class': 'django_db_logging.handlers.AsyncDBHandler',
        },

    },
    'loggers': {
        'django': {
            'level': level,
            'handlers': ['console'],
            'propagate': False,
        },
        'gunicorn': {
            'level': level,
            'handlers': ['console'],
            'propagate': False,
        },
        'celery': {
            'level': level,
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'django.template': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'social_django': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django_auth_ldap': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'ldap': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'django_db_logging': {
            'handlers': ['console'],  # do not use 'db' here
            'propagate': False,  # do not propagate
            'level': 'ERROR'
        },
        'bitcaster': {
            'level': level,
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        # 'bitcaster.config.environ': {
        #     'level': 'ERROR',
        #     'handlers': ['console', 'sentry'],
        #     'propagate': False,
        # },
        # 'bitcaster.backends.ldap': {
        #     'handlers': ['console'],
        #     'propagate': False,
        #     'level': 'DEBUG'
        # },
        # 'bitcaster.dispatchers': {
        #     'handlers': ['db'],
        #     'propagate': True,
        #     'level': 'ERROR'
        # },
        # 'bitcaster.tasks': {
        #     'handlers': ['db', 'sentry'],
        #     'propagate': True,
        #     'level': 'ERROR'
        # },
    },
}
