from django.db import models
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn


class PluginManager(models.Manager):
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
        # if registry:
        self.exclude(handler__in=registry).update(enabled=False)
        return self.all()


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

    # def __str__(self):
    #     return self.fqn
