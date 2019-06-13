from django.db import models
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster.framework.db.managers import SmartManager


class PluginManager(SmartManager):
    def is_enabled(self, *args, **kwargs):
        return self.get(*args, **kwargs).enabled

    def enable_valid(self):
        registry = self.model._meta.get_field('handler').registry
        for handler in registry:
            self.update_or_create(fqn=fqn(handler), defaults={'enabled': True})
        return self.all()

    def enabled(self):
        return self.filter(enabled=True)

    def inspect(self):
        registry = self.model._meta.get_field('handler').registry
        for handler in registry:
            is_core = fqn(handler).startswith('bitcaster.')
            self.get_or_create(fqn=fqn(handler),
                               defaults=dict(is_core=is_core,
                                             handler=fqn(handler),
                                             description=handler.help,
                                             enabled=True,
                                             version=handler.version)
                               )
        # for record in self.all():
        #     if not record.handler:
        #         record.delete()

        self.exclude(handler__in=registry).update(enabled=False)
        return self.all()

    def get_by_natural_key(self, fqn):
        return self.get(fqn=fqn)


class Plugin(models.Model):
    fqn = models.CharField(_('Name'), max_length=2000, unique=True)
    enabled = models.BooleanField(default=True)
    version = models.CharField(max_length=64)
    description = models.TextField()
    is_core = models.BooleanField(default=True)

    objects = PluginManager()

    class Meta:
        app_label = 'bitcaster'
        abstract = True
        ordering = ('fqn',)
        verbose_name = _('Plugin')
        verbose_name_plural = _('Plugins')

    def __str__(self):
        return self.fqn

    def natural_key(self):
        return (self.fqn,)
