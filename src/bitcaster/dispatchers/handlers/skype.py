from logging import getLogger

import skpy.main
from django.core.exceptions import ObjectDoesNotExist

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, RecipientNotFound
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class Message(MessageType):
    pass


class SkypeOptions(DispatcherOptions):
    username = serializers.CharField()
    password = PasswordField()


class SkypeSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Skype(CoreDispatcher):
    subscription_class = SkypeSubscription
    options_class = SkypeOptions
    message_class = MessageType
    __help__ = ''

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

    def emit(self, address: str, subject: str, message: str,
             connection=None, *args, **kwargs) -> str:
        try:
            logger.debug(f"Processing '{address}'")
            connection = connection or self._get_connection()
            recipient = connection.contacts[address]
            if not recipient:
                raise PluginSendError('Invalid Skype address %s ' % address)
            ch = recipient.chat  # 1-to-1 conversation
            ch.sendMsg(message)  # plain-text message
            return address
        except skpy.core.SkypeApiException as e:
            if e.args[1].status_code == 404:
                raise RecipientNotFound(e) from e
            logger.error(e)
            raise PluginSendError(e) from e
        except ObjectDoesNotExist as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError('Unable to find valid address for Skype: %s' % e) from e
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError('Unable to send Skype message to %s: %s' % (address, e)) from e

    def test_connection(self, raise_exception=False):
        sk = skpy.main.Skype(self.config['username'],
                             self.config['password'])
        sk.user
        return True
