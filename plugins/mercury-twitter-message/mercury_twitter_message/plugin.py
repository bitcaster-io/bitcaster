# -*- coding: utf-8 -*-

from mercury.api.fields import PasswordField
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions, )
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginValidationError, PluginSendError
from mercury.logging import getLogger
from mercury.utils.language import classproperty
from python_twitter import api

logger = getLogger('mercury.plugins.twitter')


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
    __author__ = 'unknown'
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
