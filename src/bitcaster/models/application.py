import logging
from uuid import uuid4

from django.core import validators
from django.db import models
from django.db.models import QuerySet, UUIDField
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

from bitcaster.file_storage import app_media_root
from bitcaster.framework.db.fields import (APP_ROLES, AvatarField,
                                           EncryptedJSONField,)
from bitcaster.framework.db.validators import RESERVED_NAMES, RateLimitValidator
from bitcaster.utils.slug import slugify_instance

from .base import AbstractModel
from .mixins import ReverseWrapperMixin
from .organization import Organization
from .organizationgroup import OrganizationGroup
from .user import User
from .validators import ListValidator

logger = logging.getLogger(__name__)

RESERVED_APPLICATION_NAME = frozenset(RESERVED_NAMES)

RESERVED_APPLICATION_SLUGS = frozenset(RESERVED_NAMES)


class Application(AbstractModel, ReverseWrapperMixin):
    """Application """

    DEF_MESSAGE = """This message has been sent only to the Application Admins
---
"""

    uuid = UUIDField(default=uuid4, editable=False, blank=False, null=False)
    organization = models.ForeignKey(Organization,
                                     related_name='applications',
                                     on_delete=models.CASCADE)
    name = models.CharField(_('name'),
                            max_length=300,
                            null=False,
                            validators=[
                                ListValidator(RESERVED_APPLICATION_NAME),
                                validators.RegexValidator(r'^[\w -]+$',
                                                          _('Enter a valid name.'),
                                                          'invalid')])

    slug = models.SlugField(blank=True)
    timezone = TimeZoneField(default='UTC')

    avatar = AvatarField(upload_to=app_media_root)
    picture_height = models.IntegerField(editable=False, null=True)
    picture_width = models.IntegerField(editable=False, null=True)
    enabled = models.BooleanField(default=True)

    storage = EncryptedJSONField(_('storage'), default=dict)

    rate_limit = models.CharField(max_length=100,
                                  null=True, default=None, blank=True,
                                  validators=[RateLimitValidator()])

    limit_to_groups = models.ManyToManyField(OrganizationGroup,
                                             blank=True,
                                             help_text='limit access to this application only to selected groups')

    manageable_groups = models.BooleanField(null=False, default=False,
                                            help_text='Managers can change allowed groups. '
                                                      'Otherwise only admins can.')
    core = models.BooleanField(default=False)

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
        super().save(force_insert, force_update, using, update_fields)

    def add_member(self, org_member, role):
        from bitcaster.models import ApplicationUser
        if isinstance(org_member, User):
            org_member = self.organization.memberships.get(user=org_member)

        if not isinstance(org_member, (list, QuerySet)):
            org_member = [org_member]
        for m in org_member:
            ApplicationUser.objects.update_or_create(application=self,
                                                     org_member=m,
                                                     defaults=dict(
                                                         role=role))

    @property
    def channels(self):
        from .channel import Channel
        return Channel.objects.selectable(self.organization)

    @property
    def owners(self):
        return self.organization.owners

    @property
    def members(self):
        return User.objects.filter(memberships__applications__application=self)

    @cached_property
    def admins(self):
        return User.objects.filter(memberships__applications__application=self,
                                   memberships__applications__role=APP_ROLES.ADMIN)
