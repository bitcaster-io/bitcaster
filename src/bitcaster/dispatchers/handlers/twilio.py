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


class TwilioSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


class TwilioOptions(DispatcherOptions):
    sid = serializers.CharField(allow_blank=False, required=True)
    token = serializers.CharField(allow_blank=False, required=True)
    sender = PhoneNumberField()


@dispatcher_registry.register
class Twilio(CoreDispatcher):
    __help__ = _("""

You need a valid [Twilio](https://www.twilio.com/) account to use this service.

- Get your token at https://www.twilio.com/console
- Get twilio number  at https://www.twilio.com/console/phone-numbers/incoming

""")

    name = 'SMS (Twilio)'
    subscription_class = TwilioSubscription
    options_class = TwilioOptions
    message_class = MessageType

    def _get_connection(self) -> Client:
        return Client(self.config['sid'],
                      self.config['token'])

    def emit(self, address: str, subject: str, message: str,
             connection=None, *args, **kwargs) -> str:
        try:
            connection = connection or self._get_connection()
            connection.messages.create(
                # to=address.encode('utf8'),
                to=address,
                from_=self.config['sender'].encode('utf8'),
                body=message
            )
            return address
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        connection = self._get_connection()
        return connection.api.signing_keys(self.config['sid'])
