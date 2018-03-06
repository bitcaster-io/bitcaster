# -*- coding: utf-8 -*-
from enum import Enum

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mercury import logging
from mercury.db.fields import DeletionStatusField, Role, RoleField
from mercury.file_storage import MediaFileSystemStorage, org_media_root
from mercury.utils import locks
from mercury.utils.retries import TimedRetryPolicy
from mercury.utils.slug import slugify_instance

from .base import AbstractModel

logger = logging.getLogger(__name__)


class OrganizationRole(Enum):
    OWNER = 99
    ADMIN = 90
    MEMBER = 50
    RECIPIENT = 40

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value


RESERVED_NAMES = frozenset((
    'add', 'edit', 'remove', 'delete', 'del',
    'bitcaster', 'sax', 'mercury',
    'admin', 'manage', 'login', 'account', 'register', 'api',
    'accept', 'organization', 'organizations', 'teams', 'projects', 'help',
    'docs', 'logout', '404', '500', '_static', 'out', 'debug',
    'remote', 'get-cli', 'blog', 'welcome', 'features',
    'customers', 'integrations', 'signup', 'pricing',
    'subscribe', 'enterprise', 'about', 'jobs', 'thanks', 'guide',
    'privacy', 'security', 'terms', 'from', 'sponsorship', 'for',
    'at', 'platforms', 'branding', 'vs', 'answers', '_admin',
    'support', 'register', 'user', 'profile',
))

RESERVED_ORGANIZATION_NAME = frozenset(RESERVED_NAMES)
RESERVED_ORGANIZATION_SLUGS = frozenset(RESERVED_NAMES)


class OrganizationManager(models.Manager):
    pass


class Organization(AbstractModel):
    """
    An organization represents a group of individuals which maintain ownership of applications.
    """
    name = models.CharField(_("Name"), max_length=64)
    slug = models.SlugField(_("Short name"), unique=True, blank=True)
    status = DeletionStatusField()
    date_added = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='mercury.OrganizationMember',
                                     through_fields=('organization', 'user'))
    billing_email = models.EmailField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='+')

    avatar = models.ImageField(blank=True, null=True,
                               # upload_to="pictures",
                               upload_to=org_media_root,
                               storage=MediaFileSystemStorage(),
                               height_field='picture_height',
                               width_field='picture_width'
                               )
    picture_height = models.IntegerField(editable=False, null=True)
    picture_width = models.IntegerField(editable=False, null=True)
    is_core = models.BooleanField(editable=False, default=False)
    default_role = RoleField(default=Role.MEMBER)

    objects = OrganizationManager()

    def __str__(self):
        return self.name

    @property
    def invitations(self):
        return self.memberships.filter(user__isnull=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            lock = locks.get('slug:organization', duration=5)
            with TimedRetryPolicy(10, lock.acquire):
                slugify_instance(self, self.name,
                                 reserved=RESERVED_ORGANIZATION_SLUGS)
                super(Organization, self).save(*args, **kwargs)
        else:
            super(Organization, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.is_core:
            raise Exception('You cannot delete the the default organization.')
        return super(Organization, self).delete()

    def has_access(self, user, access=None):
        queryset = self.members.filter(user=user)
        if access is not None:
            queryset = queryset.filter(type__lte=access)

        return queryset.exists()

    def add_member(self, user, role=OrganizationRole.RECIPIENT, **kwargs):
        from mercury.models import OrganizationMember
        return OrganizationMember.objects.get_or_create(organization=self,
                                                        user=user,
                                                        role=int(role),
                                                        **kwargs
                                                        )[0]
