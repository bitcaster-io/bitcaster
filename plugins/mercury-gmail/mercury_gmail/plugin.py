# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import serializers

from mercury.exceptions import PluginValidationError
from mercury.logging import getLogger

from mercury.dispatchers.base import DispatcherOptions, MessageType
from mercury.dispatchers.email import Email
from mercury.dispatchers.registry import dispatcher_registry

# logger = getLogger(__name__)


class EmailMessage(MessageType):
    pass


class GmailOptions(DispatcherOptions):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    sender = serializers.EmailField(required=True)
    timeout = serializers.IntegerField(default=60)


@dispatcher_registry.register
class Gmail(Email):
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

    def test_connection(self, raise_exception=False):
        try:
            return super().test_connection(raise_exception)
        except Exception as e:
            raise Exception("%s. Have you set Application password at "
                            "https://myaccount.google.com/apppasswords ?" % e) from e
