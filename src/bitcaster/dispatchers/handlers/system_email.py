from logging import getLogger

from constance import config
from django.conf import settings

from ..base import DispatcherOptions
from ..registry import dispatcher_registry
from .email import Email

logger = getLogger(__name__)


class EmailOptions(DispatcherOptions):
    pass


@dispatcher_registry.register
class SystemEmail(Email):
    options_class = EmailOptions
    icon = 'email'
    __help__ = 'Email dispatcher that uses system account to '

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
