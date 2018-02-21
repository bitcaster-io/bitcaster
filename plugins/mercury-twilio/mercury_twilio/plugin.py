# -*- coding: utf-8 -*-
from rest_framework import serializers
from twilio.rest import Client

from mercury.api.fields import PhoneNumberField
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger

logger = getLogger('mercury.plugins.twilio')


class Message(MessageType):
    pass


class TwilioSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


class TwilioOptions(DispatcherOptions):
    sid = serializers.CharField(allow_blank=False, required=True)
    token = serializers.CharField(allow_blank=False, required=True)
    sender = PhoneNumberField()


@dispatcher_registry.register
class Twilio(Dispatcher):
    name = 'Twilio'
    subscription_class = TwilioSubscription
    options_class = TwilioOptions
    message_class = MessageType

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = TwilioSubscription(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def _get_connection(self) -> Client:
        return Client(self.config['sid'],
                      self.config['token'])

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            self.validate_subscription(subscription)
            recipient = subscription.config['recipient']
            connection = connection or self._get_connection()
            connection.messages.create(
                to=recipient.encode('utf8'),
                from_=self.config['sender'].encode('utf8'),
                body=message.encode('utf8')
            )
            return 1
        except Exception as e:  # pragma: no cover
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        connection = self._get_connection()
        return connection.api.signing_keys(self.config['sid'])
