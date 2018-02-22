# -*- coding: utf-8 -*-
from fbchat import Client, Message
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions, )
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import (PluginSendError, PluginValidationError,
                                RecipientNotFound, )
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.facebook')


class FacebookMessage(MessageType):
    pass


class FacebookOptions(DispatcherOptions):
    key = serializers.CharField()
    password = serializers.CharField()


class FacebookSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Facebook(Dispatcher):
    subscription_class = FacebookSubscription
    options_class = FacebookOptions
    message_class = FacebookMessage
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Facebook'

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     ser = FacebookSubscription(data=subscription.config)
    #     if not ser.is_valid():
    #         raise PluginValidationError(ser.errors)
    #
    def _get_connection(self) -> Client:
        return Client(self.config['key'].encode('utf8'),
                      self.config['password'].encode('utf8'),
                      max_tries=1)

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            recipient = subscription.config['recipient']
            logger.info(f"Processing {subscription} to {recipient}")
            connection = connection or self._get_connection()

            friends = connection.searchForUsers(recipient)
            if not friends:
                raise RecipientNotFound(recipient)
            friend = friends[0]
            msg = Message(text=message.encode('utf8'))
            connection.send(msg, friend.uid)
            return 1
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        try:
            self._get_connection()
            return True
        except Exception as e:
            return False
