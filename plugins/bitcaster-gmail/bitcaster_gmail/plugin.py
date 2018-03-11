# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import serializers

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers.base import DispatcherOptions, MessageType
from bitcaster.dispatchers.email import Email
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginValidationError


class EmailMessage(MessageType):
    pass


class GmailOptions(DispatcherOptions):
    username = serializers.CharField(required=True)
    password = PasswordField(allow_blank=True, required=False)
    sender = serializers.EmailField(required=True)
    timeout = serializers.IntegerField(default=60)


@dispatcher_registry.register
class Gmail(Email):
    __core__ = False
    options_class = GmailOptions
    message_class = EmailMessage

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
                self.logger.error("Invalid configuration")
                raise PluginValidationError(opts.errors)

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        super().validate_subscription(subscription, *args, **kwargs)

    def test_connection(self, raise_exception=False):
        try:
            return super().test_connection(raise_exception)
        except Exception as e:
            raise Exception("%s. Have you set Application password at "
                            "https://myaccount.google.com/apppasswords ?" % e) from e
