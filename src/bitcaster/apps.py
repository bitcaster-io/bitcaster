import os
import re
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from flags import conditions
from flags.conditions.registry import _conditions

from bitcaster.state import state
from bitcaster.utils.http import get_server_host


@conditions.register("development mode")
def development(**kwargs: Any) -> bool:
    return settings.DEBUG and get_server_host() in ["127.0.0.1", "localhost"]


@conditions.register("server_address")
def server_address(value: str, **kwargs: Any) -> bool:
    return state.request.get_host() == value


@conditions.register("Environment Variable")
def env_var(value: str, **kwargs: Any) -> bool:
    if "=" in value:
        key, value = value.split("=")
        return os.environ.get(key, -1) == value  # noqa: PLW1508
    return value.strip() in os.environ


@conditions.register("HTTP Request Header")
def header_key(value: str, **kwargs: Any) -> bool:
    if "=" in value:
        key, value = value.split("=")
        key = f"HTTP_{key.strip()}"
        try:
            return bool(re.compile(value).match(state.request.META.get(key, "")))
        except re.error:
            return False
    else:
        value = f"HTTP_{value.strip()}"
        return value in state.request.META


class Config(AppConfig):
    verbose_name = "Bitcaster"
    name = "bitcaster"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa

        from . import checks  # noqa
        from . import tasks  # noqa
        from . import handlers as global_handlers  # noqa
        from .cache import handlers as cache_handlers  # noqa

        for cond in ["parameter", "path matches", "after date", "before date", "anonymous"]:
            if cond in _conditions:  # pragma: no branch
                del _conditions[cond]
