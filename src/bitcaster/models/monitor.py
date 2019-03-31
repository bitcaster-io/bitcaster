# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster.framework.db.fields import AgentField, EncryptedJSONField

from .application import Application
from .base import AbstractModel
from .mixins import ReverseWrapperMixin
from .organization import Organization

logger = logging.getLogger(__name__)


class MonitorQuerySet(models.QuerySet):
    def valid(self):
        return self.all()

    # def selectable(self, application):
    #     return self.filter(Q(organization=application.organization) |
    #                        Q(system=True) |
    #                        Q(application=application))
    #
    # def enabled(self, application):
    #     return self.filter(application=application,
    #                        )


class Monitor(ReverseWrapperMixin, AbstractModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization,
                                     null=True,
                                     blank=True,
                                     related_name='monitors',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey(Application,
                                    null=True,
                                    blank=True,
                                    related_name='monitors',
                                    on_delete=models.CASCADE)
    config = EncryptedJSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = AgentField(null=True)
    deprecated = models.BooleanField(default=False)
    errors_threshold = models.IntegerField(default=100,
                                           help_text='Number or errors before channel will be automatically disabled')
    objects = MonitorQuerySet().as_manager()

    class Meta:
        app_label = 'bitcaster'
        ordering = ('name',)
        unique_together = (('organization', 'application', 'name'),)
        verbose_name = _('Monitor')
        verbose_name_plural = _('Monitors')

    class Reverse:
        pattern = 'app-monitor-{op}'
        args = ['organization.slug', 'application.slug', 'id']

    def __repr__(self):
        return f'<Monitor #{self.id} {self.name}>'

    def __str__(self):
        return self.name

    @cached_property
    def handler_name(self):
        return fqn(self.handler)

    @property
    def is_configured(self):
        if self.handler:
            return self.handler.validate_configuration(self.config, False)
        return False

    def clean(self):
        if not self.handler and self.enabled:
            raise ValidationError('Cannot enable Monitor without handler')
        super().clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.handler:
            self.config = self.handler.get_full_config(self.config)
        self.organization = self.application.organization
        super().save(force_insert, force_update, using, update_fields)
