# -*- coding: utf-8 -*-
import tweepy

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher,
                                        DispatcherOptions, MessageType,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError
from bitcaster.logging import getLogger
from bitcaster.plugins.validators import MaxBodyLengthValidator
from bitcaster.templatetags.markdown import markdown
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class TwitterMessage(MessageType):
    validators = [
        MaxBodyLengthValidator(140, 'Twitter message can be max %(limit_value)s chars. (it has %(cleaned)d).')]


class TwitterOptions(DispatcherOptions):
    account = serializers.CharField()
    consumer_key = serializers.CharField()
    consumer_secret = PasswordField()
    access_token_key = PasswordField()
    access_token_secret = PasswordField()


# class TwitterSubscriptionOptions(SubscriptionOptions):
#     pass
#
# """
# 1. We are using Twitter’s APIs to send notification messages to internal registered users.
# 2. We do not analyse tweets.
# 3. Our use case involves sending tweets and direct messages but not liking or retweet.
# 4. This is only a sending system and messages will be read using the official Twitter application
# """


@dispatcher_registry.register
class Twitter(CoreDispatcher):
    options_class = TwitterOptions
    message_class = TwitterMessage
    subscription_class = None
    __help__ = """

- Apply for a developer accout at [https://developer.twitter.com/en/apply-for-access]
- Create a new app at [https://apps.twitter.com/]
- Generate your keys and configure the Channel
"""

    @classproperty
    def name(cls):
        return 'Twitter'

    def _get_connection(self) -> tweepy.API:
        config = self.owner.config
        auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
        auth.set_access_token(config['access_token_key'], config['access_token_secret'])
        return tweepy.API(auth)

    def get_usage_message(self, config: DispatcherOptions) -> object:
        return markdown('Remeber to follow [{0}](https://twitter.com/{0}) '
                        'to receive messages.'.format(config['account']))

    @classmethod
    def validate_address(cls, address, *args, **kwargs) -> bool:
        return True

    def get_recipient_address(self, subscription):
        addr = super().get_recipient_address(subscription)
        if addr.startswith('@'):
            return addr[1:]
        return addr

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            api = self._get_connection()
            api.update_status(status=message)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        try:
            api = self._get_connection()
            msg = api.update_status(status='test message')
            api.destroy_status(id=msg.id)
            return True
        except Exception as e:
            logger.exception(e)
            return False


@dispatcher_registry.register
class TwitterDirectMessage(Twitter):
    icon = 'twitter'

    @classproperty
    def name(cls):
        return 'Twitter Direct Message'

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            api = self._get_connection()
            recipient = self.get_recipient_address(subscription)
            user = api.get_user(recipient)
            event = {
                'event': {
                    'type': 'message_create',
                    'message_create': {
                        'target': {
                            'recipient_id': user.id
                        },
                        'message_data': {
                            'text': message
                        }
                    }
                }
            }
            api.send_direct_message_new(event)
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)
