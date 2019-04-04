from logging import getLogger
from urllib.parse import urlencode

import requests
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from sentry_sdk import capture_message

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError
from bitcaster.utils import fqn
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
    bot_name = serializers.CharField()
    bot_token = PasswordField()


class TelegramAccountValidator:
    def __call__(self, value):
        if value:
            try:
                return int(value)
            except Exception:
                pass
        if not value.startswith('@'):
            raise ValidationError('This should be a chat_id number or Telegram account name')


class TelegramSubscriptionOptions(SubscriptionOptions):
    # recipient = serializers.CharField(validators=[RegexValidator('^@',
    #                                                              'username must starts  with @')])
    recipient = serializers.CharField(validators=[TelegramAccountValidator()])


@dispatcher_registry.register
class Telegram(CoreDispatcher):
    options_class = TelegramOptions
    message_class = TelegramMessage
    icon = 'telegram'
    subscription_class = TelegramSubscriptionOptions
    __help__ = _("""
### Creating your bot
1. On Telegram, search @BotFather, send him a “/start” message
2. Send another “/newbot” message, then follow the instructions to setup a name and a username
3. Your bot is now ready, be sure to save a backup of your API token, and correct
""")

    @classproperty
    def name(cls):
        return 'Telegram'

    def _get_connection(self) -> requests.Session:
        s = requests.Session()

        s.headers = {'user-agent': 'bitcaster'}
        return s

    def get_usage_message(self) -> object:
        return """Send a message to %s to receive notifications.
Check your username under menu->settings.
*Note:* Accounts without username are not supported

""" % self.config['bot_name']

    def _get_url(self, method, **params):
        base = 'https://api.telegram.org/bot' + self.config['bot_token']
        return base + '/%s?%s' % (method, urlencode(params))

    def _get_chat_id_for_username(self, subscription):
        if hasattr(subscription, 'subscriber'):
            user = subscription.subscriber
        elif hasattr(subscription, 'assignments'):
            user = subscription
        else:
            raise ValueError
        chat_id = user.storage.get(fqn(self), None)
        username = self.get_recipient_address(subscription)
        if not chat_id:
            logger.info('No chat_id')
            url = self._get_url('getUpdates')
            conn = self._get_connection()
            response = conn.get(url)
            data = response.json()
            for update in data['result']:
                if update['message']['from']['username'] == username[1:]:  # username starts with @
                    chat_id = update['message']['from']['id']
                    user.storage[fqn(self)] = chat_id
                    user.save()
                    break
            else:
                raise PluginSendError('Unable to get chat_id')
        return (chat_id, username)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            # username = self.get_recipient_address(subscription)
            chat_id, username = self._get_chat_id_for_username(subscription)
            conn = self._get_connection()
            url = self._get_url('sendMessage', chat_id=chat_id,
                                text=message)
            ret = conn.get(url)
            if ret.status_code != 200:
                capture_message(ret.content)
                raise PluginSendError(ret.content)
            return username
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
