import multiprocessing

DRAMATIQ_BROKER2 = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://localhost:6379",
    },
    "MIDDLEWARE": [
        # "dramatiq.middleware.Prometheus",
        # "dramatiq.middleware.AgeLimit",
        # "dramatiq.middleware.TimeLimit",
        # "dramatiq.middleware.Callbacks",
        # "dramatiq.middleware.Retries",
    ],
}

DRAMATIQ_PROCESSES = multiprocessing.cpu_count
DRAMATIQ_THREADS = 1

DRAMATIQ_BROKER = "redis://localhost:6379/0"

DRAMATIQ_BEAT_SCHEDULE = {"beat_heartheart": {"task": "bitcaster.tasks.beat_heartbeat", "schedule": "*/5 * * * *"}}

DRAMATIQ_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s"},
        "front_door": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s from %(ip)s to %(path)s"},
        "cli": {"format": "%(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "cli"},
        "null": {"class": "logging.NullHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "dramatiq": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
