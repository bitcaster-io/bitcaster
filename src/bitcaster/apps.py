from typing import TYPE_CHECKING, Any

from django.apps import AppConfig
from django.conf import settings
from flags import conditions

from bitcaster.utils.http import get_server_host

if TYPE_CHECKING:
    from bitcaster.types.http import AnyRequest


@conditions.register("development")
def development(path: str, request: "AnyRequest", **kwargs: Any) -> bool:
    return settings.DEBUG and get_server_host() in ["127.0.0.1", "localhost"]


@conditions.register("server_address")
def server_address(value: str, request: "AnyRequest", **kwargs: Any) -> bool:
    return request.get_host() == value


class Config(AppConfig):
    verbose_name = "Bitcaster"
    name = "bitcaster"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from bitcaster.admin import register  # noqa

        from . import handlers  # noqa
