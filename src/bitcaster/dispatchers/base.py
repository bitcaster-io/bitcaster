# from rest_framework import serializers
import abc
from logging import getLogger

from bitcaster import get_full_version
from bitcaster.configurable import ConfigurableMixin, ConfigurableOptionsForm
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


class DispatcherOptions(ConfigurableOptionsForm):
    pass


class Dispatcher(ConfigurableMixin, metaclass=abc.ABCMeta):
    subscription_class = SubscriptionOptions
    options_class = DispatcherOptions
    message_class = MessageType
    need_verification = True
    handle_attachments = False
    icon = None
    verbose_name = None
    __media__ = None
    __help__ = ''

    def __init__(self, owner=None):
        super().__init__(owner)
        self.logger = getLogger('bitcaster.plugins.%s' % self.name)

    @classproperty
    def label(self):
        return self.verbose_name or self.__name__

    @abc.abstractmethod
    def _get_connection(self) -> object:
        pass  # pragma: no-cover

    def get_usage_message(self) -> str:
        """ return a message to the User to extra informations to complete the subscription.
        ie. follow Twitter
        """
        return ''

    def get_usage(self) -> str:
        """ return a message to the User to extra informations to complete the subscription.
        ie. follow Twitter
        """
        return self.get_usage_message()

    def get_recipient_address(self, subscription):
        if isinstance(subscription, str):
            raise ValueError(subscription)
        if hasattr(subscription, 'subscriber'):  # models.Subscription
            self.current_user = subscription.subscriber
        elif hasattr(subscription, 'assignments'):  # models.User
            self.current_user = subscription
        else:
            raise ValueError()
        return self.current_user.assignments.get_address(self).address

    @abc.abstractmethod
    def emit(self, address: str, subject: str, message: str,
             connection=None, silent=True, *args, **kwargs) -> str:
        """

        :param subscription: bitcaster.models.Subscription
        :param connection: object
        :param subject: message subject
        :param message: message body
        :return: recipient used
        """
        pass  # pragma: no-cover

    def validate_message(self, message, **kwargs):
        for validator in self.message_class.validators:
            validator(message, **kwargs)
        return True

    @classmethod
    def validate_address(cls, address, *args, **kwargs) -> bool:
        cls.subscription_class().fields['recipient'].run_validators(address)
        return True

    @abc.abstractmethod
    def test_connection(self, raise_exception=False):
        pass


class CoreDispatcher(Dispatcher):
    __license__ = 'MIT'
    __author__ = 'Bitcaster'
    __core__ = True
    __version__ = get_full_version(False)
    __url__ = 'http://bitcaster.io'
