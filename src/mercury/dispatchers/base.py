# from rest_framework import serializers
import abc

from mercury.configurable import ConfigurableMixin, get_full_config
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
    options_class = DispatcherOptions
    message_class = MessageType

    __media__ = None

    def __init__(self, owner=None):
        super().__init__(owner)
        self.logger = getLogger('mercury.plugins.%s' % self.name)

    @abc.abstractmethod
    def _get_connection(self) -> object:
        """

        :param subscription: mercury.models.Subscription
        :param subject: message subject
        :param message: message body
        :return:
        """
        pass  # pragma: no-cover

    @abc.abstractmethod
    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        """

        :param subscription: mercury.models.Subscription
        :param connection: object
        :param subject: message subject
        :param message: message body
        :return:
        """
        pass  # pragma: no-cover

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        cfg = get_full_config(self.subscription_class, subscription.config)
        return self.subscription_class(data=cfg).is_valid(True)

    def validate_config(self, config, *args, **kwargs) -> None:
        cfg = get_full_config(self.options_class, config)
        return self.options_class(data=cfg).is_valid(True)

    @abc.abstractmethod
    def test_connection(self, raise_exception=False):
        pass

    #
    # def log(self, message, level=INFO):
    #     self.logger.log(level, message)

    def test_message(self, subscription, subject, message, *args, **kwargs):
        # assert subscription.event is None
        assert subscription.pk is None
        return self.emit(subscription, subject, message, *args, **kwargs)
