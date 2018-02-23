# -*- coding: utf-8 -*-
import requests
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, PluginValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.twitter')


class TwitterMessage(MessageType):
    pass


class TwitterOptions(DispatcherOptions):
    pass


class TwitterSubscriptionOptions(SubscriptionOptions):
    recipient = serializers.CharField(validators=[])


@dispatcher_registry.register
class Twitter(Dispatcher):
    options_class = TwitterOptions
    message_class = TwitterMessage
    subscription_class = TwitterSubscriptionOptions
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Twitter'

    def _get_connection(self):
        s = requests.Session()
        s.headers = {'user-agent': 'mercury',
                     'Content-type': 'application/json'}
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
            payload = {
                "event": {
                    "type": "message_create",
                    "message_create": {
                        "target": {
                            "recipient_id": "844385345234"
                        },
                        "message_data": {
                            "text": "Hello World!",
                        }
                    }
                }
            }
            url = '/1.1/direct_messages/events/new.json'
            ret = conn.post(url, json=payload)
            if ret.status_code != 200:
                raise PluginSendError(ret.content)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        raise NotImplementedError
