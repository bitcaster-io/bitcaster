import os
from typing import Any

from .. import env

SYSTEM_LEVEL = env("LOGGING_LEVEL")


def get_logging_level(logger: str, default: str = "") -> str:
    key = f"LOGGING_LEVEL_{logger.upper()}"
    return os.environ.get(key, default or SYSTEM_LEVEL)


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
        "null": {"class": "logging.NullHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": SYSTEM_LEVEL,
    },
    "loggers": {
        "environ": {
            "handlers": ["console"],
            "level": get_logging_level("environ"),
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": get_logging_level("django"),
            "propagate": False,
        },
        "parso": {
            "handlers": ["null"],
            "level": get_logging_level("parso"),
            "propagate": False,
        },
        "cssutils": {
            "handlers": ["console"],
            "level": get_logging_level("cssutils"),
            "propagate": False,
        },
        "social_core": {
            "handlers": ["console"],
            "level": get_logging_level("social_core"),
            "propagate": False,
        },
        "redis": {
            "handlers": ["console"],
            "level": get_logging_level("redis"),
        },
        "bitcaster": {
            "handlers": ["console"],
            "level": get_logging_level("bitcaster"),
            "propagate": False,
        },
        "bitcaster.runner": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}


def _apply_dynamic_logging_levels(logging_dict: dict[str, Any]) -> None:
    for k, v in os.environ.items():
        if k.startswith("LOGGING_LEVEL_") and v:
            # Es. map "LOGGING_LEVEL_DJANGO__SERVER" -> "django.server"
            entry: str = k.replace("LOGGING_LEVEL_", "").lower().replace("__", ".")
            if entry in logging_dict["loggers"]:
                logging_dict["loggers"][entry]["level"] = v
            else:
                logging_dict["loggers"][entry] = {
                    "handlers": ["console"],
                    "level": v,
                    "propagate": False,
                }


_apply_dynamic_logging_levels(LOGGING)
