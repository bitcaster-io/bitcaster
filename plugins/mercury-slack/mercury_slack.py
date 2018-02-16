# -*- coding: utf-8 -*-
from rest_framework import serializers

from mercury.exceptions import PluginValidationError, PluginSendError

from mercury.logging import getLogger
from mercury.dispatchers.base import Dispatcher, DispatcherOptions, MessageType
from mercury.dispatchers.registry import dispatcher_registry

logger = getLogger(__name__)


class Message(MessageType):
    pass


class SlackOptions(DispatcherOptions):
    token = serializers.CharField()
    channel = serializers.CharField()
    fallback_to_channel = serializers.BooleanField(required=False)


class SlackSubscription(DispatcherOptions):
    regipient = serializers.CharField()


@dispatcher_registry.register
class Slack(Dispatcher):
    name = 'Slack'
    subscription_class = SlackSubscription
    options_class = SlackOptions
    message_class = MessageType

    def _get_connection(self):
        from slackclient import SlackClient
        return SlackClient(self.config['token'])

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = SlackSubscription(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            self.logger.debug(f"Emitting {subscription}")
            recipient = subscription.config['recipient']
            connection = connection or self._get_connection()

            ret = connection.api_call(
                "chat.postMessage",
                channel=recipient,
                text=message
            )
            if not ret['ok']:
                raise PluginSendError(f"Error sending to {subscription.subscriber} "
                                      f"using recipient '{recipient}' "
                                      f"Error was: {ret['error']} ")
        except Exception as e:
            logger.exception(e)
            raise
        return 1

    def test_connection(self, raise_exception=False):
        if not self.client.rtm_connect:
            raise PluginValidationError('')
