# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from fbchat import Client, Message

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (Dispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, RecipientNotFound
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger('bitcaster.plugins.facebook')


class FacebookMessage(MessageType):
    pass


class FacebookOptions(DispatcherOptions):
    key = serializers.CharField()
    password = PasswordField()


validate_username = RegexValidator(r'/^[a-z\d.]{5,}$/i',
                                   message=_('Use a valid facebook account'))


class FacebookSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Facebook(Dispatcher):
    subscription_class = FacebookSubscription
    options_class = FacebookOptions
    message_class = FacebookMessage
    __license__ = 'MIT'
    __author__ = 'Bitcaster'
    __core__ = True

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
            recipient = self.get_recipient_address(subscription)
            logger.info(f'Processing {subscription} to {recipient}')
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
        except Exception:
            return False
