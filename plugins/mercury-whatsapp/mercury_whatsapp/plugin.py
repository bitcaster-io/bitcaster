# -*- coding: utf-8 -*-
from rest_framework import serializers

from mercury.dispatchers.base import Dispatcher, DispatcherOptions, MessageType
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, ValidationError
from mercury.logging import getLogger

from .client import Client

logger = getLogger('mercury.plugins.whatsapp')


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    login = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)


# yowsup-cli registration --phone 393457466010 --cc 39 --requestcode sms --mcc 222 --mnc 01 --env android
# yowsup-cli registration --phone 393457466010 --cc 39 --register 146186 --env android

@dispatcher_registry.register
class WhatsApp(Dispatcher):
    name = 'WhatsApp'
    options_class = Options
    message_class = Message

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        pass

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0} ({1})'.format(subscription, recipient))

            client = Client(login=self.config['login'],
                            password=self.config['password']
                            )
            client.send_message(recipient, message.encode('utf8'))
            # client.send_media(phone_to, path='/Users/tax/Desktop/logo.jpg')
        except Exception as e:
            raise PluginSendError() from e


    def test_connection(self, raise_exception=False):
        raise NotImplementedError
