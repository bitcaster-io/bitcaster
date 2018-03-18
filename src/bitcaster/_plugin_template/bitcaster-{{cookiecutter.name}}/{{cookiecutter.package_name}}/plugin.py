# -*- coding: utf-8 -*-
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (Dispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, PluginValidationError
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger('bitcaster.plugins.{{cookiecutter.name}}')


class {{cookiecutter.classname}}Message(MessageType):
    pass


class {{cookiecutter.classname}}Options(DispatcherOptions):
    pass


class {{cookiecutter.classname}}SubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class {{cookiecutter.classname}}(Dispatcher):
    options_class = {{cookiecutter.classname}}Options
    message_class = {{cookiecutter.classname}}Message
    subscription_class = {{cookiecutter.classname}}SubscriptionOptions
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return '{{cookiecutter.classname}}'

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
