from typing import Any

from django.apps import AppConfig
from django.conf import settings
from flags import conditions

from bitcaster.state import state
from bitcaster.utils.http import get_server_host


@conditions.register("development")
def development(**kwargs: Any) -> bool:
    return settings.DEBUG and get_server_host() in ["127.0.0.1", "localhost"]


@conditions.register("server_address")
def server_address(value: str, **kwargs: Any) -> bool:
    return state.request.get_host() == value


class Config(AppConfig):
    verbose_name = "Bitcaster"
    name = "bitcaster"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa

        from . import handlers  # noqa
        from . import tasks  # noqa
        from .cache import handlers as cache_handlers  # noqa
