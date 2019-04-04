from logging import getLogger

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from twilio.rest import Client

from bitcaster.api.fields import PhoneNumberField
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError

logger = getLogger(__name__)


class Message(MessageType):
    pass


class TwilioWhatsAppSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


class TwilioWhatsAppOptions(DispatcherOptions):
    sid = serializers.CharField(allow_blank=False, required=True)
    token = serializers.CharField(allow_blank=False, required=True)
    sender = PhoneNumberField()


@dispatcher_registry.register
class TwilioWhatsApp(CoreDispatcher):
    __help__ = _("""

You need a valid [Twilio](https://www.twilio.com/) account to use this service.

- Get your token at [[https://www.twilio.com/console]]
- Get twilio number  at [[https://www.twilio.com/console/phone-numbers/incoming]]
- Get twilio SMS number  at [[https://www.twilio.com/console/sms/getting-started/build]]

""")
    icon = 'whatsapp'
    name = 'WhatsApp (Twilio)'
    subscription_class = TwilioWhatsAppSubscription
    options_class = TwilioWhatsAppOptions
    message_class = MessageType

    def _get_connection(self) -> Client:
        return Client(self.config['sid'],
                      self.config['token'])

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            self.validate_subscription(subscription)
            recipient = self.get_recipient_address(subscription)
            connection = connection or self._get_connection()
            connection.messages.create(
                to='whatsapp:' + recipient,
                from_='whatsapp:' + self.config['sender'],
                body=message
            )
            return recipient
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        connection = self._get_connection()
        return connection.api.signing_keys(self.config['sid'])
