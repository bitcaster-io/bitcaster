# -*- coding: utf-8 -*-
from mercury.exceptions import ValidationError

from mercury.logging import getLogger
from mercury.dispatchers.base import Dispatcher, DispatcherOptions, MessageType
from mercury.dispatchers.registry import dispatcher_registry

logger = getLogger(__name__)


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    pass


@dispatcher_registry.register
class Hangout(Dispatcher):
    name = 'Hangout'
    options_class = Options
    message_class = Message

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        if not user.email:
            raise ValidationError

    def emit(self, recipient, subject, message, *args, **kwargs):
        logger.info('%s %s %s' % (recipient, subject, message))

    def test_connection(self, raise_exception=False):
        raise NotImplementedError
