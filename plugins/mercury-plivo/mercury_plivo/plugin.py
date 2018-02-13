# -*- coding: utf-8 -*-
import plivo

from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions, )
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.plivo')


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    sid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    sender = serializers.CharField(required=True)


class PlivoSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Plivo(Dispatcher):
    subscription_class = PlivoSubscription
    options_class = DispatcherOptions
    message_class = MessageType
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Plivo'

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = PlivoSubscription(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))
            client = plivo.RestClient(auth_id=self.config['sid'],
                                      auth_token=self.config['token'])
            client.messages.create(
                src=self.config['source'],
                dst=recipient,
                text=message
            )
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        raise NotImplementedError
