# -*- coding: utf-8 -*-

from constance import config
from django.conf import settings
from django.core.mail import get_connection

from .base import DispatcherOptions
from .email import Email
from .registry import dispatcher_registry

# logger = getLogger(__name__)


class EmailOptions(DispatcherOptions):
    pass


@dispatcher_registry.register
class SystemEmail(Email):
    __core__ = True
    options_class = EmailOptions

    def _get_connection(self) -> object:
        return get_connection(
            backend=settings.EMAIL_BACKEND,
            host=config.EMAIL_HOST,
            username=config.EMAIL_HOST_USER,
            password=config.EMAIL_HOST_PASSWORD,
            port=config.EMAIL_HOST_PORT,
            use_tls=config.EMAIL_USE_TLS,
            fail_silently=False)
