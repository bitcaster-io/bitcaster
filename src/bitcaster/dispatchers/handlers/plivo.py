from logging import getLogger

import plivo

from bitcaster.api.fields import PhoneNumberField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError

logger = getLogger(__name__)


class PlivoMessage(MessageType):
    pass


class PlivoOptions(DispatcherOptions):
    sid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    sender = serializers.CharField(required=True)


class PlivoSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


@dispatcher_registry.register
class Plivo(CoreDispatcher):
    subscription_class = PlivoSubscription
    options_class = PlivoOptions
    message_class = PlivoMessage

    name = 'SMS (Plivo)'

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     ser = self.subscription_class(data=subscription.config)
    #     if not ser.is_valid():
    #         raise PluginValidationError(ser.errors)

    def _get_connection(self) -> plivo.RestClient:
        return plivo.RestClient(auth_id=self.config['sid'],
                                auth_token=self.config['token'])

    def emit(self, address: str, subject: str, message: str,
             connection=None, *args, **kwargs) -> str:
        try:
            logger.debug(f"Processing '{address}'")
            connection = connection or self._get_connection()

            ret = connection.messages.create(
                src=self.config['sender'],
                dst=address,
                text=message
            )
            if 'message_uuid' not in ret:
                raise PluginSendError(ret)
            return address
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        return conn.request('GET', '/')
