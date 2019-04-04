from bitcaster.framework.db.fields import AgentField, DispatcherField

from .plugin import Plugin


class DispatcherMetaData(Plugin):
    handler = DispatcherField(null=True, unique=True)


class AgentMetaData(Plugin):
    handler = AgentField(null=True)
