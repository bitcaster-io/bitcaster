# -*- coding: utf-8 -*-

from constance import config
from django.conf import settings

from ..base import DispatcherOptions
from ..registry import dispatcher_registry
from .email import Email

# logger = getLogger(__name__)


class EmailOptions(DispatcherOptions):
    pass


@dispatcher_registry.register
class SystemEmail(Email):
    __core__ = True
    options_class = EmailOptions
    icon = 'email'

    # def _configure(self):
    #     return super()._configure()

    @property
    def config(self):
        return dict(server=config.EMAIL_HOST,
                    port=config.EMAIL_HOST_PORT,
                    username=config.EMAIL_HOST_USER,
                    password=config.EMAIL_HOST_PASSWORD,
                    tls=config.EMAIL_USE_TLS,
                    sender=config.EMAIL_SENDER,
                    timeout=30,
                    backend=settings.EMAIL_BACKEND,
                    )

    # def _get_connection(self) -> object:
    #     return get_connection(
    #         backend=settings.EMAIL_BACKEND,
    #         host=config.EMAIL_HOST,
    #         username=config.EMAIL_HOST_USER,
    #         password=config.EMAIL_HOST_PASSWORD,
    #         port=config.EMAIL_HOST_PORT,
    #         use_tls=config.EMAIL_USE_TLS,
    #         fail_silently=False)
