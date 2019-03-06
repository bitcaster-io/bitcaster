# from rest_framework import serializers
import abc

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster import get_full_version
from bitcaster.configurable import ConfigurableMixin, get_full_config
from bitcaster.exceptions import PluginValidationError
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

from . import serializers

logger = getLogger(__name__)


class MessageType:
    has_subject = False
    allow_html = False
    max_size = None
    allow_attachment = False
    max_attachment_size = None
    validators = []


class SubscriptionOptions(serializers.Serializer):
    recipient = serializers.CharField()


class DispatcherOptions(serializers.Serializer):
    pass


class Dispatcher(ConfigurableMixin, metaclass=abc.ABCMeta):
    subscription_class = SubscriptionOptions
    options_class = DispatcherOptions
    message_class = MessageType
    icon = None
    __media__ = None
    __help__ = _('')

    def __init__(self, owner=None):
        super().__init__(owner)
        self.logger = getLogger('bitcaster.plugins.%s' % self.name)

    @classproperty
    def fqn(cls):
        return fqn(cls)

    @abc.abstractmethod
    def _get_connection(self) -> object:
        pass  # pragma: no-cover

    def get_usage_message(self, config: DispatcherOptions) -> object:
        """ return a message to the User to extra informations to complete the subscription.
        ie. follow Twitter
        """
        return ''

    def get_usage(self, config: DispatcherOptions) -> object:
        """ return a message to the User to extra informations to complete the subscription.
        ie. follow Twitter
        """
        return self.get_usage_message(config)

    def get_recipient_address(self, subscription):
        if isinstance(subscription, str):
            return subscription
        user = subscription.subscriber
        try:
            return subscription.config['recipient']
        except (KeyError, TypeError):
            return user.assignments.get_address(self)

    @abc.abstractmethod
    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        """

        :param subscription: bitcaster.models.Subscription
        :param connection: object
        :param subject: message subject
        :param message: message body
        :return:
        """
        pass  # pragma: no-cover

    def validate_message(self, message, **kwargs):
        for validator in self.message_class.validators:
            validator(message, **kwargs)

    @classmethod
    def validate_address(cls, address, *args, **kwargs) -> bool:
        cls.subscription_class().fields['recipient'].run_validators(address)
        return True

    def validate_subscription(self, subscription, *args, **kwargs) -> bool:
        if isinstance(subscription, str):
            return True
        cfg = get_full_config(self.subscription_class, subscription.config)
        cfg['recipient'] = self.get_recipient_address(subscription)
        try:
            return self.subscription_class(data=cfg).is_valid(True)
        except (serializers.ValidationError, ValidationError) as e:
            raise PluginValidationError(str(e)) from e

    @abc.abstractmethod
    def test_connection(self, raise_exception=False):
        pass  # pragma: no-cover

        # try:
        #     self._get_connection()
        #     return True
        # except Exception as e:
        #     logger.exception(e)
        #     return False

    def test_message(self, subscription, subject, message, *args, **kwargs):
        # assert subscription.event is None
        assert subscription.pk is None
        return self.emit(subscription, subject, message, *args, **kwargs)


class CoreDispatcher(Dispatcher):
    __license__ = 'MIT'
    __author__ = 'Bitcaster'
    __core__ = True
    __version__ = get_full_version(False)
    __url__ = 'http://bitcaster.io'
