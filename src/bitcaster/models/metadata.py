# -*- coding: utf-8 -*-
from django.db import models
from strategy_field.utils import fqn

from bitcaster.agents.registry import agent_registry
from bitcaster.db.fields import AgentField, DispatcherField
from bitcaster.exceptions import HandlerNotFound

from .plugin import Plugin


def handler_not_found(field, fqn, exc):
    raise HandlerNotFound(fqn)


class DispatcherMetaData(Plugin):
    handler = DispatcherField(null=True, unique=True, import_error=handler_not_found)


class AgentManager(models.Manager):
    def inspect(self):
        for handler in agent_registry:
            is_core = fqn(handler).startswith('bitcaster.')
            self.update_or_create(name=fqn(handler),
                                  defaults=dict(is_core=is_core,
                                                handler=fqn(handler),
                                                description=handler.__help__,
                                                enabled=False,
                                                version=handler.__version__)
                                  )

    def register(self, url):
        pass

    def unregister(self, name):
        pass


class AgentMetaData(Plugin):
    handler = AgentField(null=True)
