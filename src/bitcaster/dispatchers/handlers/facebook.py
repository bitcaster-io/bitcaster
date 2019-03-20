# -*- coding: utf-8 -*-
from logging import getLogger

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from fbchat import Client, Message

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError, RecipientNotFound
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class FacebookMessage(MessageType):
    pass


class FacebookOptions(DispatcherOptions):
    account = serializers.CharField()
    key = serializers.CharField()
    password = PasswordField()


validate_username = RegexValidator(r'/^[a-z\d.]{5,}$/i',
                                   message=_('Use a valid facebook account'))


class FacebookSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


@dispatcher_registry.register
class Facebook(CoreDispatcher):
    subscription_class = FacebookSubscription
    options_class = FacebookOptions
    message_class = FacebookMessage
    __help__ = _("""Configure Channel

- goto [https://developers.facebook.com/apps/](https://developers.facebook.com/apps/)
 and create a new app that represent your Biscaster instance
- If you see **Become a Facebook developer** message click on `Register Now` and complete registration.
- Select `Get Started with the Pages API`
- get `App ID` and `App Secret`

""")

    @classproperty
    def name(cls):
        return 'Facebook'

    def get_usage_message(self, **kwargs) -> object:
        return _('To receive messages thru Facebook chat, '
                 'you must add {config[account]} to your Facebook friends list.').format(self=self,
                                                                                         config=self.config,
                                                                                         **kwargs)

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
        except RecipientNotFound as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(_('User %(user)s is not a friend of this Facebook account').format(user=e))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        try:
            self._get_connection()
            return True
        except Exception:
            return False
