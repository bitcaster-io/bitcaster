# -*- coding: utf-8 -*-
from bitcaster.utils.language import classproperty

from ..base import CoreDispatcher
from ..registry import dispatcher_registry


@dispatcher_registry.register
class ConsoleDispatcher(CoreDispatcher):
    __help__ = 'Simple Dispatcher that emit on standard output'

    def emit(self, **kwargs):
        print(**kwargs)

    def validate_user(self, user, *args, **kwargs) -> None:
        pass

    def test_connection(self, raise_exception=False):
        pass

    @classproperty
    def name(self):
        return 'Console'

    def _get_connection(self) -> object:
        pass

    @classmethod
    def validate_address(cls, address, *args, **kwargs):
        return True

    def validate_subscription(self, subscription, *args, **kwargs):
        return subscription.config == {}
