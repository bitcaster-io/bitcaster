# -*- coding: utf-8 -*-
import skpy.main
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, ValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.skype')


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    username = serializers.CharField()
    password = serializers.CharField()


class RecipientOptions(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Skype(Dispatcher):
    options_class = Options
    message_class = Message
    subscription_class = RecipientOptions
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Skype'

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = RecipientOptions(data=subscription.config)
        if not ser.is_valid():
            raise ValidationError(ser.errors)

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
