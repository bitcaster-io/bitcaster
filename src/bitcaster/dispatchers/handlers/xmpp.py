# -*- coding: utf-8 -*-
from pyxmpp2.simple import send_message

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (Dispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class Message(MessageType):
    pass


class XmppOptions(DispatcherOptions):
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)


class XmppSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Xmpp(Dispatcher):
    subscription_class = XmppSubscription
    options_class = XmppOptions
    message_class = MessageType
    __core__ = True
    __license__ = 'MIT'
    __author__ = 'Bitcaster'

    @classproperty
    def name(cls):
        return 'Xmpp'

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     ser = XmppSubscription(data=subscription.config)
    #     if not ser.is_valid():
    #         raise PluginValidationError(ser.errors)

    def _get_connection(self) -> object:
        pass
        # settings = XMPPSettings({
        #     "software_name": "Echo Bot"
        # })
        # return Client(self.config['username'], [self, ], settings)

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            recipient = self.get_recipient_address(subscription)
            logger.debug(f"Processing {subscription} '{recipient}'")
            send_message(self.config['username'],
                         self.config['password'],
                         recipient,
                         message)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        return True
