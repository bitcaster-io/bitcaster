# -*- coding: utf-8 -*-

from django.core.handlers.wsgi import WSGIRequest

import requests
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.oauth import OAauthHAndler
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.slack-oauth')


class SlackOAuthMessage(MessageType):
    pass


def validate_recipient(value):
    if not (value.startswith('@') or value.startswith('#')):
        raise PluginValidationError("Invalid recipient")


class SlackOAuthOptions(DispatcherOptions):
    client_id = serializers.CharField()
    sender = serializers.CharField(validators=[validate_recipient])
    legacy = serializers.CharField()
    credentials = serializers.JSONField(read_only=True)


class SlackOAuthSubscription(SubscriptionOptions):
    recipient = serializers.CharField(validators=[validate_recipient])


class SlackOAuthHandler(OAauthHAndler):
    authorization_url = 'https://slack.com/oauth/authorize'
    fetch_token_url = 'https://slack.com/api/oauth.access'
    authority = 'Slack'
    client_id = '15398619125.312378638625'
    scopes = 'identify,chat:write:user'
    # authorization_extra_kwargs = {'team': 'sax'}
    fetch_token_extra_kwargs = {'client_id': client_id,
                                'client_secret': 'e9f2d4c1542f6f3a87cb0ed1290ff922',
                                }

    def _get_state(self, request: WSGIRequest, redirect_to=None):
        return super()._get_state(request, redirect_to)

    # def render_button(self):
    #     return '<img alt="Add to Slack" height="40" width="139" ' \
    #            'src="https://platform.slack-edge.com/img/add_to_slack.png" ' \
    #            'srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x,' \
    #            'https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" />'


@dispatcher_registry.register
class SlackOAuth(Dispatcher, SlackOAuthHandler):
    options_class = SlackOAuthOptions
    message_class = SlackOAuthMessage
    subscription_class = SlackOAuthSubscription
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'SlackOAuth'

    def _get_connection(self):
        s = requests.Session()

        s.headers = {'user-agent': 'mercury',
                     "authorization": "Bearer %s" % self.config['credentials']['access_token']
                     }
        return s

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = SlackOAuthSubscription(data=subscription.config)
        if not ser.is_valid():
            raise PluginValidationError(ser.errors)

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            self.logger.debug(f"Emitting {subscription.id}")
            recipient = subscription.config['recipient']
            connection = connection or self._get_connection()
            params = {
                "channel": recipient,
                "text": message,
                "as_user": "true",
                "username": self.config['sender'],
            }
            response = connection.post(f"https://slack.com/api/chat.postMessage",
                                       params)
            ret = response.json()
            if not ret['ok']:
                raise PluginSendError(f"Error sending to {subscription.subscriber} "
                                      f"using recipient '{recipient}' "
                                      f"Error was: {ret['error']} ")
        except Exception as e:
            logger.exception(e)
            raise
        return 1

    def test_message(self, subscription, subject, message, *args, **kwargs):
        assert subscription.pk is None
        return self.emit(subscription, subject, message, *args, **kwargs)

    def test_connection(self, raise_exception=False):
        try:
            connection = self._get_connection()

            if not connection.rtm_connect:
                raise PluginValidationError('')
            return connection
        except Exception as e:
            logger.exception(e)
            raise
