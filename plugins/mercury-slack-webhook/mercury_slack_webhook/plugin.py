# -*- coding: utf-8 -*-
import requests
from django.conf.urls.static import static
from django.utils.translation import ugettext as _

from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.slack-webhook')


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
class SlackWebhook(Dispatcher):
    options_class = SlackWebhookOptions
    message_class = SlackWebhookMessage
    subscription_class = SlackWebhookSubscriptionOptions
    __license__ = 'MIT'
    __author__ = 'unknown'
    __help__ = """To use this plugin you need to enable the `Incoming WebHooks`
 application in you Slack console.
Navigate to https://<YOUR_SPACE>.slack.com/apps/" and enable `Incoming WebHooks`.

"""

    @classproperty
    def name(cls):
        return 'SlackWebHook'

    def _get_connection(self):
        s = requests.Session()

        s.headers = {'user-agent': 'mercury'}
        return s

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = self.subscription_class(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))
            conn = self._get_connection()
            ret = conn.post(self.config['url'],
                            json={'username': self.config['bot_name'],
                                  'icon_url': self.config['icon_url'],
                                  'channel': recipient,
                                  'text': message,
                                  }
                            )
            if ret.status_code != 200:
                raise PluginSendError(ret.content)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e) from e

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        return conn
