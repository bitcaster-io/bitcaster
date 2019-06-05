from logging import getLogger

from slack import WebClient

from bitcaster.api.fields import PasswordField
from bitcaster.exceptions import PluginSendError
from bitcaster.utils.language import classproperty

from .. import serializers
from ..base import (CoreDispatcher, DispatcherOptions,
                    MessageType, SubscriptionOptions,)
from ..registry import dispatcher_registry

logger = getLogger(__name__)


class SlackMessage(MessageType):
    pass


class SlackOptions(DispatcherOptions):
    api_token = PasswordField()


class SlackSubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class Slack(CoreDispatcher):
    options_class = SlackOptions
    message_class = SlackMessage
    subscription_class = SlackSubscriptionOptions
    icon = 'slack'
    __help__ = """To use this plugin you need to create a BOT application in your workspace.
 - Build or edit your app at [[https://api.slack.com/apps]]
 - Add a `Bot User` to your app
 - Add `chat:write:bot` permission scope
"""
    __core__ = True

    @classproperty
    def name(cls):
        return 'Slack'

    def _get_connection(self):
        return WebClient(token=self.config['api_token'])

    def emit(self, address, subject, message, connection=None, *args, **kwargs):
        try:
            conn = connection or self._get_connection()
            conn.chat_postMessage(channel=address,
                                  as_user=True,
                                  text=message)
            return address
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e) from e

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        return conn
