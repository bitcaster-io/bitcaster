# -*- coding: utf-8 -*-
from rest_framework import serializers

from mercury.exceptions import ValidationError

from mercury.logging import getLogger
from mercury.dispatchers.base import Dispatcher, DispatcherOptions, MessageType
from mercury.dispatchers.registry import dispatcher_registry
from twilio.rest import Client

logger = getLogger('mercury.plugins.twilio')


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    sid = serializers.CharField(allow_blank=False, required=True)
    token = serializers.CharField(allow_blank=False, required=True)
    sender = serializers.CharField(allow_blank=False, required=True)


@dispatcher_registry.register
class Twilio(Dispatcher):
    name = 'Twilio'
    options_class = Options
    message_class = Message

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        pass

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
