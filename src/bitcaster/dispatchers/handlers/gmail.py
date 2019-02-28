# -*- coding: utf-8 -*-
from logging import getLogger

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers.base import DispatcherOptions, MessageType
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginValidationError

from .email import Email

logger = getLogger(__name__)


class EmailMessage(MessageType):
    has_subject = True
    allow_html = True


class GmailOptions(DispatcherOptions):
    username = serializers.CharField(required=True)
    password = PasswordField(allow_blank=True, required=False)
    sender = serializers.EmailField(required=True)
    timeout = serializers.IntegerField(default=60)


@dispatcher_registry.register
class Gmail(Email):
    options_class = GmailOptions
    message_class = EmailMessage
    icon = None
    __help__ = _("""Simplified Email dispatcher for GMail accounts.

**Generate Application password**

- Navigate to your [Google Account](https://myaccount.google.com/security).
- Under the Password & sign-in method section, click App passwords.
- If requested login again using your usual password.
- Make sure Other (custom name) is selected in the Select app drop-down menu.
 Type the application name (ie. Bitcaster)
- Click Generate.
""")

    def _configure(self):
        if self.options_class:
            opts = self.options_class(data=self.owner.config)
            if opts.is_valid():
                data = dict(opts.data)
                data['backend'] = settings.EMAIL_BACKEND
                data['server'] = 'smtp.gmail.com'
                data['port'] = 587
                data['tls'] = True
                return data
            else:
                self.logger.error('Invalid configuration')
                raise PluginValidationError(opts.errors)

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     super().validate_subscription(subscription, *args, **kwargs)

    def test_connection(self, raise_exception=False):
        try:
            return super().test_connection(raise_exception)
        except Exception as e:
            raise Exception('%s. Have you set Application password at '
                            'https://myaccount.google.com/apppasswords ?' % e) from e
