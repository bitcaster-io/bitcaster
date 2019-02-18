# -*- coding: utf-8 -*-
from django.db import models
from strategy_field.utils import fqn

from bitcaster.db.fields import MonitorField
from bitcaster.monitor.registry import monitor_registry

from .plugin import Plugin


class MonitorManager(models.Manager):
    def inspect(self):
        for handler in monitor_registry:
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


class MonitorMetaData(Plugin):
    handler = MonitorField(null=True)
