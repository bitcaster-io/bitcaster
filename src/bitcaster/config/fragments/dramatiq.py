from ..settings import env

DRAMATIQ_BROKER = env("DRAMATIQ_BROKER")

LEVEL = "DEBUG"

DRAMATIQ_LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s"},
        "front_door": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s from %(ip)s to %(path)s"},
        "cli": {"format": "%(asctime)s %(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "cli"},
        "cli": {"class": "logging.StreamHandler", "formatter": "cli"},
        "null": {"class": "logging.NullHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": LEVEL,
    },
    "loggers": {
        "dramatiq.worker": {
            "handlers": ["cli"],
            "propagate": False,
            "level": LEVEL,
        },
        "dramatiq": {
            "handlers": ["cli"],
            "propagate": False,
            "level": LEVEL,
        },
        "bitcaster": {
            "handlers": ["cli"],
            "level": LEVEL,
            "propagate": False,
        },
    },
}
