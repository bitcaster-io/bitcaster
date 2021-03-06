from logging import getLogger

import requests
from django.conf.urls.static import static
from django.utils.translation import ugettext_lazy as _

from bitcaster.exceptions import PluginSendError
from bitcaster.utils.language import classproperty

from .. import serializers
from ..base import (CoreDispatcher, DispatcherOptions,
                    MessageType, SubscriptionOptions,)
from ..registry import dispatcher_registry

logger = getLogger(__name__)


class SlackWebhookMessage(MessageType):
    pass


class SlackWebhookOptions(DispatcherOptions):
    url = serializers.URLField(help_text=_('Your custom Slack webhook URL.'))
    bot_name = serializers.CharField(required=False,
                                     allow_blank=True,
                                     help_text=_('The name used when publishing messages.')
                                     )
    icon_url = serializers.URLField(required=False,
                                    allow_blank=True,
                                    help_text='''The url of the icon to appear beside your bot (32px png), leave empty for none.
You may use {}'''.format(static('logos/bitcaster32.png')))
    # channel = serializers.CharField(help_text='Optional #channel name or @user')


class SlackWebhookSubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class SlackWebhook(CoreDispatcher):
    options_class = SlackWebhookOptions
    message_class = SlackWebhookMessage
    subscription_class = SlackWebhookSubscriptionOptions
    icon = 'slack.png'
    __help__ = """To use this plugin you need to enable the `Incoming WebHooks`
 application in you Slack console.
Navigate to https://<YOUR_SPACE>.slack.com/apps/" and enable `Incoming WebHooks`.

"""
    __core__ = True

    @classproperty
    def name(cls):
        return 'SlackWebHook'

    def _get_connection(self):
        s = requests.Session()

        s.headers = {'user-agent': 'bitcaster'}
        return s

    def emit(self, address, subject, message, *args, **kwargs):
        try:
            # url = "https://slack.com/api/chat.postMessage"
            logger.debug(f"Processing '{address}'")
            conn = self._get_connection()
            ret = conn.post(self.config['url'],
                            json={'username': self.config['bot_name'],
                                  'icon_url': self.config['icon_url'],
                                  'channel': address,
                                  'text': message,
                                  }
                            )
            if ret.status_code != 200:
                raise PluginSendError(ret.content.decode())
            return address
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e) from e

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        return conn
