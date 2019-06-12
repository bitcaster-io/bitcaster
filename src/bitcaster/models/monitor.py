import logging

from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster.framework.db.fields import AgentField, EncryptedJSONField
from bitcaster.models.fields import ThrottleField
from bitcaster.tsdb.api import stats

from .base import AbstractModel
from .mixins import ReverseWrapperMixin

logger = logging.getLogger(__name__)

cache_lock = caches['lock']


class MonitorQuerySet(models.QuerySet):
    def valid(self):
        return self.all()

    def scheduled(self):
        return self.filter(enabled=True,
                           start_date__lt=timezone.now(),
                           end_date__gte=timezone.now())


class Monitor(ReverseWrapperMixin, AbstractModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey('bitcaster.Organization',
                                     null=True,
                                     blank=True,
                                     related_name='monitors',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    null=True,
                                    blank=True,
                                    related_name='monitors',
                                    on_delete=models.CASCADE)
    config = EncryptedJSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = AgentField(null=True)
    deprecated = models.BooleanField(default=False)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    max_events = models.PositiveIntegerField(blank=True, null=True)
    rate = ThrottleField(default='1/s')

    errors_threshold = models.IntegerField(default=100,
                                           help_text='Number or errors before channel will be automatically disabled')
    objects = MonitorQuerySet().as_manager()

    class Meta:
        app_label = 'bitcaster'
        ordering = ('name',)
        unique_together = (('organization', 'application', 'name'),)
        verbose_name = _('monitor')
        verbose_name_plural = _('monitors')

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

    @cached_property
    def key(self):
        return 'monitor:%s:%s:%s' % (self.organization_id, self.application_id, self.pk)

    def lock(self):
        lock = cache_lock.lock(self.key)
        return lock.acquire(False)

    def locked(self):
        return cache_lock.get(self.key)

    def unlock(self):
        lock = cache_lock.lock(self.key)
        cache_lock.delete(lock.name)

    def check_and_run(self):

        if self.lock():
            try:
                self.handler.poll()
                stats.increase(self.key)
            finally:
                self.unlock()
        else:
            logger.warning('Monitor locked')

    @property
    def is_configured(self):
        if self.handler:
            return self.handler.validate_configuration(self.config, False)
        return False

    def clean(self):
        if self.end_date and (self.start_date > self.end_date):
            raise ValidationError(_('Monitor cannot have end date before start date'))

        if not self.handler and self.enabled:
            raise ValidationError(_('Cannot enable Monitor without handler'))
        super().clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.handler:
            self.config = self.handler.get_full_config(self.config)
        self.organization = self.application.organization
        super().save(force_insert, force_update, using, update_fields)
