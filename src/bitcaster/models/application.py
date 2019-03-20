# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

# from bitfield import BitField
# from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import models
from django.db.models import UUIDField
# from django.utils.functional import cached_property
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

from bitcaster.file_storage import app_media_root
from bitcaster.framework.db.fields import (AvatarField, Role,
                                           SubscriptionPolicyField,)
from bitcaster.framework.db.validators import RESERVED_NAMES, RateLimitValidator
from bitcaster.utils.slug import slugify_instance

from .base import AbstractModel
from .mixins import ReverseWrapperMixin
from .organization import Organization
# from bitcaster.models import ApplicationRole
from .validators import ListValidator

logger = logging.getLogger(__name__)

RESERVED_APPLICATION_NAME = frozenset(RESERVED_NAMES)

RESERVED_APPLICATION_SLUGS = frozenset(RESERVED_NAMES)


class Application(AbstractModel, ReverseWrapperMixin):
    """Application """
    uuid = UUIDField(default=uuid4, editable=False, blank=False, null=False)
    organization = models.ForeignKey(Organization,
                                     related_name='applications',
                                     on_delete=models.CASCADE)
    name = models.CharField(_('Name'),
                            max_length=300,
                            null=False,
                            validators=[
                                ListValidator(RESERVED_APPLICATION_NAME),
                                validators.RegexValidator(r'^[\w -]+$',
                                                          _('Enter a valid name.'),
                                                          'invalid')],
                            unique=True)
    slug = models.SlugField(blank=True)
    timezone = TimeZoneField(default='UTC')

    avatar = AvatarField(upload_to=app_media_root)
    picture_height = models.IntegerField(editable=False, null=True)
    picture_width = models.IntegerField(editable=False, null=True)
    default_subscription_policy = SubscriptionPolicyField()
    enabled = models.BooleanField(default=True)

    rate_limit = models.CharField(max_length=100,
                                  null=True, default=None, blank=True,
                                  validators=[RateLimitValidator()])

    class Meta:
        app_label = 'bitcaster'
        ordering = ('name', 'id')

    class Reverse:
        args = ['organization.slug', 'slug']
        pattern = 'app-{op}'
        actions = ['edit', 'delete', 'dashboard']
        links = ['create', 'list']

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            slugify_instance(self, self.name,
                             reserved=RESERVED_APPLICATION_SLUGS)
        super(Application, self).save(force_insert, force_update, using, update_fields)

    @property
    def channels(self):
        from .channel import Channel
        return Channel.objects.selectable(self)

    @property
    def owners(self):
        return self.organization.owners

    @cached_property
    def admins(self):
        admins = []
        for t in self.teams.filter(roles=Role.ADMIN):
            admins.extend([m.user for m in t.members])
        return admins
