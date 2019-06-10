from bitcaster.framework.db.fields import AgentField, DispatcherField

from .plugin import Plugin, PluginManager


class DispatcherManager(PluginManager):
    pass


class DispatcherMetaData(Plugin):
    handler = DispatcherField(null=True, unique=True)
    objects = DispatcherManager()


class AgentMetaData(Plugin):
    handler = AgentField(null=True)
