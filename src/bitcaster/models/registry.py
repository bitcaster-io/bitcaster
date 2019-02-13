from django.db import models
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster.db.fields import DispatcherField
from bitcaster.dispatchers import dispatcher_registry


class RegistryManager(models.Manager):
    def inspect(self):
        for handler in dispatcher_registry:
            self.update_or_create(name=fqn(handler),
                                  defaults=dict(is_core=handler.__core__,
                                                handler=fqn(handler),
                                                description=handler.__help__,
                                                enabled=False,
                                                version=handler.__version__)
                                  )


class Registry(models.Model):
    name = models.CharField(_('Name'), max_length=64, unique=True)
    handler = DispatcherField(null=True, unique=True)
    enabled = models.BooleanField(default=True)
    version = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    is_core = models.BooleanField(default=True)

    objects = RegistryManager()

    class Meta:
        app_label = 'bitcaster'
        verbose_name_plural = 'Handlers'

    def __str__(self):
        return self.name
