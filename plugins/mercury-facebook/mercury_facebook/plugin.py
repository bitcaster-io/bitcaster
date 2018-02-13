# -*- coding: utf-8 -*-
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions, )
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, ValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

import fbchat

logger = getLogger('mercury.plugins.facebook')


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    key = serializers.CharField()
    password = serializers.CharField()


class RecipientOptions(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Facebook(Dispatcher):
    options_class = Options
    message_class = Message
    subscription_class = RecipientOptions
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Facebook'

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = RecipientOptions(data=subscription.config)
        if not ser.is_valid():
            raise ValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))
            client = fbchat.Client(self.config['key'].encode('utf8'),
                                   self.config['password'].encode('utf8'),
                                   max_tries=1)

            friends = client.searchForUsers("Giovanni Bronzini")
            friend = friends[0]
            msg = fbchat.Message(text=message.encode('utf8'))
            client.send(msg, friend.uid)
            return True
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        client = fbchat.Client(self.config['key'],
                               self.config['password'])

        return True
