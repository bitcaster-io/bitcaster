# -*- coding: utf-8 -*-
import skpy.main
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions, )
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.skype')


class Message(MessageType):
    pass


class SkypeOptions(DispatcherOptions):
    username = serializers.CharField()
    password = serializers.CharField()


class SkypeSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Skype(Dispatcher):
    subscription_class = SkypeSubscription
    options_class = SkypeOptions
    message_class = MessageType
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Skype'

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = SkypeSubscription(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))
            sk = skpy.main.Skype(self.config['username'], self.config['password'])
            ch = sk.contacts[recipient].chat  # 1-to-1 conversation
            ch.sendMsg(message)  # plain-text message
            return True
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e) from e

    def test_connection(self, raise_exception=False):
        sk = skpy.main.Skype(self.config['username'],
                             self.config['password'])
        sk.user
        return True
