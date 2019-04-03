# -*- coding: utf-8 -*-
import os
from logging import getLogger

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
# https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token
#
# for OSX with macport
# install_name_tool -change /usr/local/opt/openssl/lib/libssl.1.0.0.dylib \
#           /opt/local/lib/libssl.1.0.0.dylib \
#           <PROJECT>/~contrib/tdlib/libtdjson.dylib
# install_name_tool -change /usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib \
#           /opt/local/lib/libcrypto.1.0.0.dylib \
#           <PROJECT>/~contrib/tdlib/libtdjson.dylib
#
#
# Reference:
# https://stackoverflow.com/questions/49036478/pypy-does-not-work-on-macos-10-9-5


class TelegramMessage(MessageType):
    validators = []


class TelegramOptions(DispatcherOptions):
    api_id = serializers.CharField()
    api_hash = PasswordField()
    short_name = serializers.CharField()
    title = serializers.CharField()
    bot_token = serializers.CharField()
    encryption_key = serializers.CharField()


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
- Create new BOT following [[https://telegra.ph/Awesome-Telegram-Bot-11-11]]
""")

    @classproperty
    def name(cls):
        return 'Telegram'

    def _get_connection(self) -> Client:
        conn = Client(
            api_id=self.config['api_id'],
            api_hash=self.config['api_hash'],
            phone=self.config['bot_token'],
            use_test_dc=True,
            database_encryption_key=self.config['encryption_key'],
            library_path=os.environ.get('TD_LIB', ''),
            use_message_database=False,
            tdlib_verbosity=9,
            files_directory='/data/PROGETTI/saxix/bitcaster/mercury/~build/tdlib',
            login=True,
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
            self._get_connection()
            return True
        except Exception as e:
            logger.exception(e)
            return False
