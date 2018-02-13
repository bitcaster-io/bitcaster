# -*- coding: utf-8 -*-
from rest_framework import serializers

from mercury.exceptions import PluginValidationError

from mercury.logging import getLogger
from mercury.dispatchers.base import Dispatcher, DispatcherOptions, MessageType, SubscriptionOptions
from mercury.dispatchers.registry import dispatcher_registry
from twilio.rest import Client

logger = getLogger('mercury.plugins.twilio')


class Message(MessageType):
    pass


class TwilioSubscription(SubscriptionOptions):
    pass


class TwilioOptions(DispatcherOptions):
    sid = serializers.CharField(allow_blank=False, required=True)
    token = serializers.CharField(allow_blank=False, required=True)
    sender = serializers.CharField(allow_blank=False, required=True)


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

    @property
    def client(self):
        return Client(self.config['sid'],
                      self.config['token'])

    def emit(self, subscription, subject, message, *args, **kwargs):
        recipient = subscription.config['recipient']
        self.client.messages.create(
            to=recipient.encode('utf8'),
            from_=self.config['sender'].encode('utf8'),
            body=message.encode('utf8')
        )

    def test_connection(self, raise_exception=False):
        return self.client.api.signing_keys(self.config['sid'])
