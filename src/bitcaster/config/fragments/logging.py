import logging

import cssutils

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s"},
        "front_door": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s from %(ip)s to %(path)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "front_door": {"class": "logging.StreamHandler", "formatter": "front_door"},
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "loggers": {
        "djstripe": {
            "handlers": [
                "console",
            ],
            "level": "ERROR",
            "propagate": False,
        },
        "stripe": {
            "handlers": [
                "console",
            ],
            "level": "ERROR",
            "propagate": False,
        },
        "analytical": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "environ": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "parso": {
            "handlers": ["null"],
            "level": "WARNING",
            "propagate": False,
        },
        "cssutils": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "social_core": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "two_factor": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "redis": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        "bitcaster": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
cssutils.log.setLevel(logging.CRITICAL)
