# -*- coding: utf-8 -*-
from logging import getLogger

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

from bitcaster.api.fields import PhoneNumberField
from bitcaster.exceptions import PluginSendError
from bitcaster.state import state
from bitcaster.utils import fqn

from ..base import (CoreDispatcher, DispatcherOptions,
                    MessageType, SubscriptionOptions,)
from ..registry import dispatcher_registry

logger = getLogger(__name__)


class ViberMessage(MessageType):
    has_subject = False
    allow_html = False


class ViberSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


class ViberOptions(DispatcherOptions):
    key = serializers.CharField(help_text=_('Application Name'),
                                default='Bitcaster')
    site = serializers.URLField(help_text=_('URL where your Viber server is located.'),
                                default=lambda: state.request.get_host())
    email = serializers.EmailField(help_text=_('The email address of the user who owns the API key mentioned above.'))
    insecure = serializers.BooleanField(help_text=_('Use insecure connection'))


@dispatcher_registry.register
class ViberPrivate(CoreDispatcher):
    icon = '/bitcaster/images/icons/viber.png'
    options_class = ViberOptions
    subscription_class = ViberSubscription
    message_class = ViberMessage
    __help__ = _("""Viber dispatcher to send private message
### Get API keys

- follow the [instructions](https://viber.github.io/docs/general/get-started/) to get your keys

    https://Viberchat.com/api/incoming-webhooks-overview#incoming-webhook-integrations

    """)

    # def validate_subscription(self, subscription, *args, **kwargs) -> bool:
    #     email = self.get_recipient_address(subscription)
    #     cfg = {'recipient': self.owner.config.get('recipient', email)}
    #     try:
    #         return self.subscription_class(data=cfg).is_valid(True)
    #     except (serializers.ValidationError, ValidationError) as e:
    #         raise PluginValidationError(str(e)) from e

    def _get_connection(self) -> Api:
        config = self.config

        bot_configuration = BotConfiguration(
            name=config['name'],
            avatar='http://viber.com/avatar.jpg',
            auth_token='YOUR_AUTH_TOKEN_HERE'
        )
        return Api(bot_configuration)

    def emit(self, subscription, subject, message, connection=None, *args, **kwargs) -> int:
        recipient = self.get_recipient_address(subscription)
        try:
            conn = connection or self._get_connection()
            # Send a stream message
            request = {
                'type': 'private',
                'to': recipient,
                'content': message,
            }
            result = conn.send_message(request)
            if result['result'] != 'success':
                raise PluginSendError(result['msg'])
            self.logger.debug(f'{fqn(self)} sent to {recipient}')
            return 1
        except Exception as e:
            self.logger.exception(e)

    def test_connection(self, raise_exception=False) -> bool:
        try:
            conn = self._get_connection()
            conn.ensure_session()
            return True
        except Exception as e:
            self.logger.exception(e)
            if raise_exception:
                raise
            return False
