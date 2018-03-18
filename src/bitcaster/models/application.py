# -*- coding: utf-8 -*-
from uuid import uuid4

from bitfield import BitField
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import models
from django.db.models import UUIDField
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

from bitcaster import logging
from bitcaster.db.fields import SubscriptionPolicyField
from bitcaster.db.validators import RateLimitValidator
from bitcaster.file_storage import MediaFileSystemStorage, app_media_root
from bitcaster.utils import locks
from bitcaster.utils.retries import TimedRetryPolicy
from bitcaster.utils.slug import slugify_instance

from .base import AbstractModel
from .organization import RESERVED_NAMES, Organization

logger = logging.getLogger(__name__)

RESERVED_APPLICATION_NAME = frozenset(RESERVED_NAMES)

RESERVED_APPLICATION_SLUGS = frozenset(RESERVED_NAMES)


class Application(AbstractModel):
    """Application """
    uuid = UUIDField(default=uuid4, editable=False, blank=False, null=False)
    organization = models.ForeignKey(Organization,
                                     related_name='applications',
                                     on_delete=models.CASCADE)
    name = models.CharField(_('Name'),
                            max_length=300,
                            validators=[
                                validators.RegexValidator(r'^[\w -]+$',
                                                          _('Enter a valid name.'),
                                                          'invalid')],
                            unique=True)
    slug = models.SlugField(blank=True)
    timezone = TimeZoneField(default='UTC')
    allowed_origins = ArrayField(models.CharField(max_length=50),
                                 blank=True,
                                 null=True)
    first_event = models.DateTimeField(null=True, editable=False)
    flags = BitField(flags=(
        # ('has_releases', 'This Project has sent release data'),
    ), default=0, null=True)
    teams = models.ManyToManyField('bitcaster.Team',
                                   related_name='teams',
                                   through='bitcaster.ApplicationTeam'
                                   )

    avatar = models.ImageField(blank=True, null=True,
                               upload_to=app_media_root,
                               storage=MediaFileSystemStorage(),
                               height_field='picture_height',
                               width_field='picture_width'
                               )
    picture_height = models.IntegerField(editable=False, null=True)
    picture_width = models.IntegerField(editable=False, null=True)
    subscription_policy = SubscriptionPolicyField()
    enabled = models.BooleanField(default=True)

    rate_limit = models.CharField(max_length=100,
                                  null=True, default=None, blank=True,
                                  validators=[RateLimitValidator()])

    class Meta:
        app_label = 'bitcaster'
        ordering = ("name", "id")

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            lock = locks.get('slug:application', duration=5)
            with TimedRetryPolicy(10, lock.acquire):
                slugify_instance(self, self.name,
                                 reserved=RESERVED_APPLICATION_SLUGS)
            super(Application, self).save(force_insert, force_update, using, update_fields)
        else:
            super(Application, self).save(force_insert, force_update, using, update_fields)

    @property
    def channels(self):
        from .channel import Channel
        return Channel.objects.selectable(self)
        # return Channel.objects.filter(Q(organization=self.organization) |
        #                               Q(system=True) |
        #                               Q(application=self))

    @property
    def owners(self):
        return self.organization.owners
