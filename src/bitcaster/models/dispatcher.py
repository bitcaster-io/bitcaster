from bitcaster.db.fields import DispatcherField
from bitcaster.exceptions import HandlerNotFound

from .plugin import Plugin


def handler_not_found(field, fqn, exc):
    raise HandlerNotFound(fqn)


class DispatcherMetaData(Plugin):
    handler = DispatcherField(null=True, unique=True, import_error=handler_not_found)
