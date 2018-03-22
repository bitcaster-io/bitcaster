# -*- coding: utf-8 -*-
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (Dispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, PluginValidationError
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger('bitcaster.plugins.telegram')


class TelegramMessage(MessageType):
    pass


class TelegramOptions(DispatcherOptions):
    pass


class TelegramSubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class Telegram(Dispatcher):
    options_class = TelegramOptions
    message_class = TelegramMessage
    subscription_class = TelegramSubscriptionOptions
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Telegram'

    def _get_connection(self):
        raise NotImplementedError

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = self.subscription_class(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))
            raise NotImplementedError
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        raise NotImplementedError
