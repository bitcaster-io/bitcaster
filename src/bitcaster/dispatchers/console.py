# -*- coding: utf-8 -*-
from bitcaster.utils.language import classproperty

from .base import Dispatcher
from .registry import dispatcher_registry


@dispatcher_registry.register
class ConsoleDispatcher(Dispatcher):
    __core__ = True

    def emit(self, **kwargs):
        print(**kwargs)

    def validate_user(self, user, *args, **kwargs) -> None:
        pass

    def test_connection(self, raise_exception=False):
        pass

    @classproperty
    def name(self):
        return "Console"

    def _get_connection(self) -> object:
        pass

    def validate_subscription(self, subscription, *args, **kwargs):
        return subscription.config == {}
