from logging import getLogger

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from zulip import Client as ZulipClient

from bitcaster.exceptions import PluginSendError
from bitcaster.utils.reflect import fqn

from ..base import (CoreDispatcher, DispatcherOptions,
                    MessageType, SubscriptionOptions,)
from ..registry import dispatcher_registry

logger = getLogger(__name__)


class ZulipMessage(MessageType):
    has_subject = False
    allow_html = False


class ZulipSubscription(SubscriptionOptions):
    recipient = serializers.EmailField()


class ZulipOptions(DispatcherOptions):
    site = serializers.URLField(help_text=_('URL where your Zulip server is located.'))
    key = serializers.CharField(help_text=_("API key, which you can get through Zulip's web interface."))
    email = serializers.EmailField(help_text=_('The email address of the user who owns the API key mentioned above.'))
    insecure = serializers.BooleanField(default=True,
                                        help_text=_('Use insecure connection'))


@dispatcher_registry.register
class ZulipPrivate(CoreDispatcher):
    icon = '/bitcaster/images/icons/zulip.png'
    options_class = ZulipOptions
    subscription_class = ZulipSubscription
    message_class = ZulipMessage
    __help__ = _("""Zulip dispatcher to send private message
### Get API keys

- follow the [instructions](https://zulipchat.com/api/api-keys#get-a-bots-api-key) to get your keys

    https://zulipchat.com/api/incoming-webhooks-overview#incoming-webhook-integrations

    """)

    def _get_connection(self) -> ZulipClient:
        config = self.config

        client = ZulipClient(email=config['email'],
                             api_key=config['key'],
                             site=config['site'])
        return client

    def emit(self, address, subject, message, connection=None, *args, **kwargs) -> str:
        try:
            conn = connection or self._get_connection()
            # Send a stream message
            request = {
                'type': 'private',
                'to': address,
                'content': message,
            }
            result = conn.send_message(request)
            if result['result'] != 'success':
                raise PluginSendError(result['msg'])
            self.logger.debug(f'{fqn(self)} sent to {address}')
            return address
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
