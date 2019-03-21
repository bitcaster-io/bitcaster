# -*- coding: utf-8 -*-
from logging import getLogger

from django.conf import settings
from django.utils.translation import gettext as _
from telegram.client import Telegram as Client

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)

# Credits:
# https://github.com/alexander-akhmetov/python-telegram
# https://github.com/Bannerets/tdlib-binaries

# Reference:
# https://stackoverflow.com/questions/49036478/pypy-does-not-work-on-macos-10-9-5


class TelegramMessage(MessageType):
    validators = []


class TelegramOptions(DispatcherOptions):
    api_id = serializers.CharField()
    api_hash = PasswordField()
    short_name = serializers.CharField()
    title = serializers.CharField()


class TelegramSubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class Telegram(CoreDispatcher):
    options_class = TelegramOptions
    message_class = TelegramMessage
    icon = 'telegram'
    subscription_class = TelegramSubscriptionOptions
    __help__ = _("""

- Follow instrunction at [[https://core.telegram.org/api/obtaining_api_id]]
- Obtaining api_id at [[https://my.telegram.org/apps]]

""")

    @classproperty
    def name(cls):
        return 'Twitter'

    def _get_connection(self) -> Client:
        conn = Client(
            api_id=self.config['api_id'],
            api_hash=self.config['api_hash'],
            phone='bot_token',  # you can pass 'bot_token' instead
            database_encryption_key=settings.SECRET_KEY,
        )
        conn.login()
        return conn

    def get_usage_message(self) -> object:
        return ''

    @classmethod
    def validate_address(cls, address, *args, **kwargs) -> bool:
        return True

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            return 0
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        try:
            api = self._get_connection()
            return False
        except Exception as e:
            logger.exception(e)
            return False
