# -*- coding: utf-8 -*-
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions, )
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty
from pyxmpp2.simple import send_message

logger = getLogger('mercury.plugins.xmpp')


class Message(MessageType):
    pass


class XmppOptions(DispatcherOptions):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class XmppSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Xmpp(Dispatcher):
    subscription_class = XmppSubscription
    options_class = XmppOptions
    message_class = MessageType
    __license__ = 'MIT'
    __author__ = 'unknown'

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
            recipient = subscription.config['recipient']
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
