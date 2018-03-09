# -*- coding: utf-8 -*-
# import twitter
from django.utils.safestring import mark_safe
from python_twitter import api

from mercury.api.fields import PasswordField
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.twitter')


class TwitterMessage(MessageType):
    pass


class TwitterOptions(DispatcherOptions):
    consumer_key = serializers.CharField()
    consumer_secret = PasswordField()
    access_token_key = PasswordField()
    access_token_secret = PasswordField()


class TwitterSubscriptionOptions(SubscriptionOptions):
    pass


@dispatcher_registry.register
class Twitter(Dispatcher):
    options_class = TwitterOptions
    message_class = TwitterMessage
    subscription_class = TwitterSubscriptionOptions
    __license__ = 'MIT'
    __author__ = 'Bitcaster'
    __help__ = mark_safe("""
Get your keys at <a target='_new' href='https://apps.twitter.com/'>https://apps.twitter.com/</a>
""")

    @classproperty
    def name(cls):
        return 'Twitter'

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
            api = self._get_connection()
            api.PostUpdate(message)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        api = self._get_connection()
        try:
            api.GetBlocks()
            return True
        except Exception as e:
            logger.exception(e)
            return False
