import logging
from uuid import uuid4

from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, UUIDField
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from rest_framework.reverse import reverse

from bitcaster.framework.db.validators import RateLimitValidator
from bitcaster.models.fields import TTLDBField
from bitcaster.utils.http import absolute_uri
from bitcaster.utils.ttl import DAY

from .application import Application
from .base import AbstractModel
from .mixins import ReverseWrapperMixin
from .team import ApplicationTeam

logger = logging.getLogger(__name__)


class Event(ReverseWrapperMixin, AbstractModel):
    """Event is something that can happen into an Application."""

    POLICIES = Choices(
        (1, 'FREE', _('Free. (Everybody can automatically subscribe)')),
        (2, 'INVITATION', _('Invitation. (Require invitation. Event will not be visible)')),
        # (3, 'MEMBERS', _('Members only. (Only members of Application Teams can subscribe)')),
        (4, 'MANAGED', _('Admin managed. (Only Application Admin can subscribe/unsubscribe)'))
    )
    uuid = UUIDField(default=uuid4, editable=False)
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    related_name='events')
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=True, blank=True)
    allowed_origins = ArrayField(models.GenericIPAddressField(max_length=50),
                                 blank=True,
                                 null=True)
    group = models.CharField(max_length=30, null=True, blank=True)
    arguments = JSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    development_mode = models.BooleanField(default=False,
                                           help_text=_('Only Admins will receive events'),
                                           )
    rate_limit = models.CharField(max_length=100,
                                  null=True, default=None, blank=True,
                                  validators=[RateLimitValidator()])
    channels = models.ManyToManyField('bitcaster.Channel')
    subscription_policy = models.IntegerField(choices=POLICIES,
                                              default=POLICIES.FREE)
    limit_to_teams = models.ManyToManyField(ApplicationTeam)
    core = models.BooleanField(default=False)

    # Processing
    START_IMMEDIATLY = 1
    START_END = 2
    START_MANUALLY = 3
    batch_mode = models.IntegerField(choices=(
        (START_IMMEDIATLY, _('Start imeddiatly')),
        (START_END, _('Start when all notifications are successufully created')),
        (START_MANUALLY, _('Manually start batch, after all notifications are successufully created')),
    ), default=START_IMMEDIATLY)

    # Attachment
    attachment = models.ForeignKey('bitcaster.FileGetter',
                                   on_delete=models.SET_NULL,
                                   blank=True, null=True)
    ERROR_IGNORE = 1
    ERROR_HALT = 2
    ERROR_ABORT = 3
    attachment_policy = models.IntegerField(choices=((ERROR_IGNORE, 'Continue on missing attachent'),
                                                     (ERROR_HALT, 'Halt on Error')
                                                     ), default=ERROR_HALT)
    # Retrying
    retry_interval = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    retry_max = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Confirmation
    need_confirmation = models.BooleanField(default=False, help_text='Need read message confirmation')
    code_prefix = models.CharField(max_length=5, blank=True, null=True,
                                   db_index=True, unique=True,
                                   help_text='Prefix to use to create confirmation code')

    # Reminders
    reminders = models.IntegerField(default=0, validators=[MaxValueValidator(10),
                                                           MinValueValidator(0)])

    reminder_interval = models.IntegerField(default=30,
                                            help_text=_('Minimum interval between reminders. (minutes)'),
                                            validators=[MaxValueValidator(DAY),
                                                        MinValueValidator(1)])

    event_expiration = TTLDBField(default=DAY,
                                  help_text=_('Time to wait before any pending notification '
                                              'will be canceled. '
                                              'Format: num second|minutes|hour|day. '
                                              'ie. 1d=1 day - 30m=30 minutes'))
    allow_attachments = models.BooleanField(default=False)

    class Meta:
        app_label = 'bitcaster'
        unique_together = (('application', 'name'),)
        ordering = ('name', 'id')
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    class Reverse:
        pattern = 'app-event-{op}'
        args = ['application.organization.slug', 'application.slug', 'id']

    def get_short_api_url(self, key):
        return absolute_uri(reverse('api:application-event-tr',
                                    args=[self.application.organization.slug,
                                          self.application.pk,
                                          '%s:%s' % (key, self.pk)]))

    def get_api_url(self):
        return absolute_uri(reverse('api:application-event-trigger',
                                    args=[self.application.organization.slug,
                                          self.application.pk,
                                          self.pk]))

    def get_batch_url(self):
        return absolute_uri(reverse('api:application-event-batch',
                                    args=[self.application.organization.slug,
                                          self.application.pk,
                                          self.pk]))

    def __str__(self):
        return self.name

    @cached_property
    def valid_channels(self):
        return self.channels.filter(messages__enabled=True)

    @cached_property
    def enabled_channels(self):
        return self.channels.filter(enabled=True)

    def get_or_create_key(self):
        created = False
        key = self.application.keys.filter(Q(events=self,
                                             all_events=True)).first()
        if not key:
            key = self.application.keys.create(name=f'Auto created key for {self}')
            key.events.add(self)
        return key, created
