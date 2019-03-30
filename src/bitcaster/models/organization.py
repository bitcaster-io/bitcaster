# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.file_storage import org_media_root
from bitcaster.framework.db.fields import (ROLES, AvatarField,
                                           DeletionStatusField, RoleField,)
from bitcaster.framework.db.manager import DeleteableModelManagerMixin
from bitcaster.framework.db.validators import RESERVED_NAMES, RateLimitValidator
from bitcaster.models.mixins import ReverseWrapperMixin
from bitcaster.models.validators import ListValidator, NameValidator
# from bitcaster.utils import locks
from bitcaster.utils.slug import slugify_instance

from .base import AbstractModel

logger = logging.getLogger(__name__)

RESERVED_ORGANIZATION_NAME = frozenset(RESERVED_NAMES)
RESERVED_ORGANIZATION_SLUGS = frozenset(RESERVED_NAMES)


class OrganizationManager(DeleteableModelManagerMixin, models.Manager):
    pass


class Organization(AbstractModel, ReverseWrapperMixin):
    """
    An organization represents a group of individuals which maintain ownership of applications.
    """
    reverse_args = ['organization.slug']

    name = models.CharField(_('Name'), max_length=64,
                            validators=[
                                ListValidator(RESERVED_ORGANIZATION_NAME),
                                NameValidator()],
                            )
    slug = models.SlugField(_('Short name'), unique=True, blank=True,
                            validators=[])
    status = DeletionStatusField()
    enabled = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='bitcaster.organizationmember',
                                     through_fields=('organization', 'user'))
    admin_email = models.EmailField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='+')
    avatar = AvatarField(upload_to=org_media_root)
    picture_height = models.IntegerField(editable=False, null=True)
    picture_width = models.IntegerField(editable=False, null=True)
    is_core = models.BooleanField(editable=False, default=False)
    default_role = RoleField(default=ROLES.ADMIN)
    rate_limit = models.CharField(max_length=100,
                                  null=True, default=None, blank=True,
                                  validators=[RateLimitValidator()])

    objects = OrganizationManager()

    class Meta:
        app_label = 'bitcaster'

    class Reverse:
        args = ['slug']
        pattern = 'org-{op}'

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return self.urls.dashboard

    # @property
    # def invitations(self):
    #     return self.memberships.filter(user__isnull=True)
    #
    # def clean_slug(self, value):
    #     if not self.is_core:
    #         check_reserved(value)

    def save(self, *args, **kwargs):
        if not self.slug:
            # lock = locks.get('slug:organization', 5)
            # with TimedRetryPolicy(10, lock.acquire):
            slugify_instance(self, self.name,
                             reserved=RESERVED_ORGANIZATION_SLUGS)
        super(Organization, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.is_core:
            raise Exception('You cannot delete the the default organization.')
        return super(Organization, self).delete()

    # def has_access(self, user, access=None):
    #     queryset = self.members.filter(user=user)
    #     if access is not None:
    #         queryset = queryset.filter(type__lte=access)
    #
    #     return queryset.exists()

    def add_member(self, user, role=ROLES.SUBSCRIBER, **kwargs):
        from bitcaster.models import OrganizationMember
        return OrganizationMember.objects.update_or_create(organization=self,
                                                           user=user,
                                                           defaults={'role': int(role)},
                                                           **kwargs
                                                           )[0]

    # def membership_for(self, user):
    #     return self.memberships.filter(user=user).first()
    #
    @property
    def owners(self):
        return self.members.filter(memberships__role=ROLES.OWNER)

    @property
    def admins(self):
        admins = self.memberships.filter(role=ROLES.ADMIN)
        if admins:
            return [m.user for m in admins.all()]
        return []

    @property
    def managers(self):
        admins = self.memberships.filter(role__in=[ROLES.ADMIN, ROLES.OWNER])
        return [m.user for m in admins.all()]

    # @property
    # def channels(self):
    #     from .channel import Channel
    #     return Channel.objects.filter(Q(organization=self) | Q(system=True))
    #
    # @cached_property
    # def configured(self):
    #     return self.channels.filter(enabled=True)
