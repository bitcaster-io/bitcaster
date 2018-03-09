# -*- coding: utf-8 -*-

from python_twitter import api

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (Dispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions, )
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, PluginValidationError
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger('bitcaster.plugins.twitter')


class TwitterMessageType(MessageType):
    pass


class TwitterMessageOptions(DispatcherOptions):
    consumer_key = serializers.CharField()
    consumer_secret = PasswordField()
    access_token_key = PasswordField()
    access_token_secret = PasswordField()


class TwitterMessageSubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class TwitterMessage(Dispatcher):
    options_class = TwitterMessageOptions
    message_class = TwitterMessageType
    subscription_class = TwitterMessageSubscriptionOptions
    __license__ = 'MIT'
    __author__ = 'Bitcaster'
    __help__ = """
    https://apps.twitter.com
"""

    @classproperty
    def name(cls):
        return 'TwitterMessage'

    def _get_connection(self):

        config = self.owner.config
        return api.Api(config['consumer_key'],
                       config['consumer_secret'],
                       config['access_token_key'],
                       config['access_token_secret'], )

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = self.subscription_class(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            conn = self._get_connection()
            conn.PostDirectMessage(message, screen_name=recipient)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        try:
            conn.GetBlocks()
            return True
        except Exception as e:
            logger.exception(e)
            return False
