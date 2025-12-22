import os
import re
from typing import Any

from django.conf import settings
from flags import conditions

from bitcaster.state import state
from bitcaster.utils.http import get_server_host


@conditions.register("development mode")  # type: ignore
def development(**kwargs: Any) -> bool:
    return settings.DEBUG and get_server_host() in ["127.0.0.1", "localhost"]


@conditions.register("server_address")  # type: ignore
def server_address(value: str, **kwargs: Any) -> bool:
    return state.request.get_host() == value


@conditions.register("Environment Variable")  # type: ignore
def env_var(value: str, **kwargs: Any) -> bool:
    if "=" in value:
        key, value = value.split("=")
        return os.environ.get(key, -1) == value  # noqa: PLW1508
    return value.strip() in os.environ


@conditions.register("HTTP Request Header")  # type: ignore
def header_key(value: str, **kwargs: Any) -> bool:
    req = kwargs.get("request", state.request)
    if "=" in value:
        key, value = value.split("=")
        key = f"HTTP_{key.strip()}"
        try:
            return bool(re.compile(value).match(req.META.get(key, "")))
        except re.error:
            return False
    else:
        value = f"HTTP_{value.strip()}"
        return value in req.META
