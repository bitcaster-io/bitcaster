# -*- coding: utf-8 -*-
from rest_framework import serializers

from mercury.exceptions import ValidationError, PluginValidationError, PluginSendError

from mercury.logging import getLogger
from mercury.dispatchers.base import Dispatcher, DispatcherOptions, MessageType
from mercury.dispatchers.registry import dispatcher_registry

logger = getLogger(__name__)


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    token = serializers.CharField()
    channel = serializers.CharField()
    fallback_to_channel = serializers.BooleanField(required=False)


class RecipientOptions(DispatcherOptions):
    regipient = serializers.CharField()


@dispatcher_registry.register
class Slack(Dispatcher):
    name = 'Slack'
    options_class = Options
    message_class = Message

    @property
    def client(self):
        from slackclient import SlackClient
        return SlackClient(self.config['token'])

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = RecipientOptions(data=subscription.config)
        if not ser.is_valid():
            raise ValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        recipient = subscription.config['recipient']

        ret = self.client.api_call(
            "chat.postMessage",
            channel=recipient,
            text=message
        )
        if not ret['ok']:
            raise PluginSendError(f"Error sending to {subscription.subscriber} "
                                  f"using recipient '{recipient}' "
                                  f"Error was: {ret['error']} ")

    def test_connection(self, raise_exception=False):
        if not self.client.rtm_connect:
            raise PluginValidationError('')
