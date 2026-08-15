from typing import TYPE_CHECKING

from django.core.mail import get_connection

from .email import BaseEmailDispatcher

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import DispatcherHandler


class SystemDispatcher(BaseEmailDispatcher):
    slug = "system-email"
    verbose_name = "System Email"
    config_class = None
    backend = None

    def get_connection(self) -> "DispatcherHandler":
        return get_connection()
