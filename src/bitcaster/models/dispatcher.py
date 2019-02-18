from bitcaster.db.fields import DispatcherField

from .plugin import Plugin


class DispatcherMetaData(Plugin):
    handler = DispatcherField(null=True)
