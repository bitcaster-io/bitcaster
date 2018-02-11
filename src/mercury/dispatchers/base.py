# from rest_framework import serializers
import abc
from logging import INFO

from mercury.configurable import ConfigurableMixin
from mercury.logging import getLogger

from . import serializers

logger = getLogger(__name__)

# MEDIUM_EMAIL = 'email'
# MEDIUM_SMS = 'sms'
# MEDIUM_URL = 'url'
#
# MEDIA = [MEDIUM_EMAIL, MEDIUM_SMS, MEDIUM_URL]
# MEDIA_CHOICES = zip(MEDIA, MEDIA)


class MessageType(object):
    pass


class SubscriptionOptions(serializers.Serializer):
    pass


class DispatcherOptions(serializers.Serializer):
    pass


class Dispatcher(ConfigurableMixin, metaclass=abc.ABCMeta):
    subscription_class = SubscriptionOptions
    options_class = SubscriptionOptions
    message_class = MessageType

    __media__ = None

    def __init__(self, owner=None):
        super().__init__(owner)
        self.logger = getLogger('mercury.plugins.%s' % self.name)

    @abc.abstractmethod
    def emit(self, subscription: object, subject: str, message: str, *args, **kwargs) -> None:
        """

        :param subscription: mercury.models.Subscription
        :param subject: message subject
        :param message: message body
        :return:
        """
        pass  # pragma: no-cover

    @abc.abstractmethod
    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        pass  # pragma: no-cover

    @abc.abstractmethod
    def test_connection(self, raise_exception=False):
        pass

    def log(self, message, level=INFO):
        self.logger.log(level, message)
