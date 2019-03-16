# -*- coding: utf-8 -*-
from bitcaster.db.fields import AgentField, DispatcherField

from .plugin import Plugin


class DispatcherMetaData(Plugin):
    handler = DispatcherField(null=True, unique=True)


class AgentMetaData(Plugin):
    handler = AgentField(null=True)
