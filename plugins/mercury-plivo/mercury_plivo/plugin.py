# -*- coding: utf-8 -*-
import plivo

from mercury.api.fields import PhoneNumberField
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.plivo')


class PlivoMessage(MessageType):
    pass


class PlivoOptions(DispatcherOptions):
    sid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    sender = serializers.CharField(required=True)


class PlivoSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


@dispatcher_registry.register
class Plivo(Dispatcher):
    subscription_class = PlivoSubscription
    options_class = PlivoOptions
    message_class = PlivoMessage
    __license__ = 'MIT'
    __author__ = 'Bitcaster'

    @classproperty
    def name(cls):
        return 'Plivo'

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     ser = self.subscription_class(data=subscription.config)
    #     if not ser.is_valid():
    #         raise PluginValidationError(ser.errors)

    def _get_connection(self) -> plivo.RestClient:
        return plivo.RestClient(auth_id=self.config['sid'],
                                auth_token=self.config['token'])

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))
            connection = connection or self._get_connection()

            ret = connection.messages.create(
                src=self.config['sender'],
                dst=recipient,
                text=message
            )
            if 'message_uuid' not in ret:
                raise PluginSendError(ret)
            return 1
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        return conn.request('GET', '/')
