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
            # 'level': 'DEBUG',
            'class': 'logging.NullHandler',
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
        }
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
        'bitcaster.dispatchers.registry': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'bitcaster': {
            'level': level,
            'handlers': ['console', 'sentry'],
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
        # 'redis': {
        #     'level': 'ERROR',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # 'gunicorn': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # 'django.middleware': {
        #     'level': 'INFO',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # 'raven': {
        #     'level': 'ERROR',
        #     'handlers': ['null'],
        #     'propagate': False,
        # },
        # 'oauth2client': {
        #     'level': 'ERROR',
        #     'handlers': ['sentry'],
        #     'propagate': False,
        # },
        # 'bitcaster.security': {
        #     'level': 'INFO',
        #     'handlers': ['sentry'],
        #     'propagate': False,
        # },
        # 'bitcaster.dispatchers': {
        #     'level': 'ERROR',
        #     'handlers': ['console', 'sentry'],
        #     'propagate': False,
        # },
        # 'bitcaster.plugins': {
        #     'level': 'ERROR',
        #     'handlers': ['console', 'sentry'],
        #     'propagate': False,
        # },
    },
}
