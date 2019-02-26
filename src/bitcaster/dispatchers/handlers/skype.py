# -*- coding: utf-8 -*-
import skpy.main

from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, RecipientNotFound
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class Message(MessageType):
    pass


class SkypeOptions(DispatcherOptions):
    username = serializers.CharField()
    password = serializers.CharField()


class SkypeSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Skype(CoreDispatcher):
    subscription_class = SkypeSubscription
    options_class = SkypeOptions
    message_class = MessageType

    @classproperty
    def name(cls):
        return 'Skype'

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     ser = SkypeSubscription(data=subscription.config)
    #     if not ser.is_valid():
    #         raise PluginValidationError(ser.errors)
    #
    def _get_connection(self) -> skpy.main.Skype:
        return skpy.main.Skype(self.config['username'], self.config['password'])

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            recipient = self.get_recipient_address(subscription)
            self.logger.info('Processing {0}'.format(subscription, recipient))
            connection = connection or self._get_connection()
            ch = connection.contacts[recipient].chat  # 1-to-1 conversation
            ch.sendMsg(message)  # plain-text message
            return 1
        except skpy.core.SkypeApiException as e:
            if e.args[1].status_code == 404:
                subscription.active = False
                subscription.save()
                raise RecipientNotFound(e) from e
            logger.error(e)
            raise PluginSendError(e) from e
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e) from e

    def test_connection(self, raise_exception=False):
        sk = skpy.main.Skype(self.config['username'],
                             self.config['password'])
        sk.user
        return True
