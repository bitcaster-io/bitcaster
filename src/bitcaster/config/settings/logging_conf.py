LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'short': {
            'format': '%(levelname)-10s %(name)s '
            # '%(pathname)s'
                      ':%(lineno)d '
                      '%(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'logging.NullHandler',
            # 'formatter': 'short'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'short'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'formatter': 'short'
        }
    },
    'loggers': {
        '': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'redis_lock': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'redis': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'ERROR',
            'handlers': ['null'],
            'propagate': False,
        },
        'oauth2client': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'bitcaster.security': {
            'level': 'INFO',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'bitcaster.dispatchers': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'bitcaster.plugins': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'bitcaster': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
    },
}
