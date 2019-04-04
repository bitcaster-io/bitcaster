from bitcaster.utils.language import classproperty

from ..base import CoreDispatcher
from ..registry import dispatcher_registry


@dispatcher_registry.register
class ConsoleDispatcher(CoreDispatcher):
    __help__ = 'Simple Dispatcher that emit on standard output'

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, silent=True, *args, **kwargs) -> str:
        print(**kwargs)
        return 'console'

    @classproperty
    def name(self):
        return 'Console'

    def _get_connection(self) -> object:
        return 'Ok'

    @classmethod
    def validate_address(cls, address, *args, **kwargs):
        return True

    def validate_subscription(self, subscription, *args, **kwargs):
        return True

    def test_connection(self, raise_exception=False):
        return True
