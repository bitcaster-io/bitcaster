# -*- coding: utf-8 -*-
"""
mercury / organization
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging
from enum import Enum

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from timezone_field import TimeZoneField

from mercury.utils import locks
from mercury.utils.retries import TimedRetryPolicy
from mercury.utils.slug import slugify_instance

logger = logging.getLogger(__name__)


class OrganizationStatus(Enum):
    ACTIVE = 1
    PENDING_DELETION = 2
    DELETION_IN_PROGRESS = 3

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value


RESERVED_NAMES = frozenset(('bitcaster', 'sax', 'mercury',
                            'admin', 'manage', 'login', 'account', 'register', 'api',
                            'accept', 'organization', 'organizations', 'teams', 'projects', 'help',
                            'docs', 'logout', '404', '500', '_static', 'out', 'debug',
                            'remote', 'get-cli', 'blog', 'welcome', 'features',
                            'customers', 'integrations', 'signup', 'pricing',
                            'subscribe', 'enterprise', 'about', 'jobs', 'thanks', 'guide',
                            'privacy', 'security', 'terms', 'from', 'sponsorship', 'for',
                            'at', 'platforms', 'branding', 'vs', 'answers', '_admin',
                            'support',
                            ))

RESERVED_ORGANIZATION_NAME = frozenset(RESERVED_NAMES)
RESERVED_ORGANIZATION_SLUGS = frozenset(RESERVED_NAMES)


class OrganizationManager(models.Manager):
    # def get_by_natural_key(self, slug):
    #     return self.get(slug=slug)

    def get_for_user(self, user, scope=None, only_visible=True):
        """
        Returns a set of all organizations a user has access to.
        """
        from mercury.models import OrganizationMember

        if not user.is_authenticated():
            return []

        if settings.SENTRY_PUBLIC and scope is None:
            if only_visible:
                return list(self.filter(status=OrganizationStatus.VISIBLE))
            else:
                return list(self.filter())

        qs = OrganizationMember.objects.filter(user=user).select_related('organization')
        if only_visible:
            qs = qs.filter(organization__status=OrganizationStatus.VISIBLE)

        results = list(qs)

        if scope is not None:
            return [
                r.organization for r in results
                if scope in r.get_scopes()
            ]
        return [r.organization for r in results]


class Organization(models.Model):
    """
    An organization represents a group of individuals which maintain ownership of applications.
    """
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True, blank=True)
    status = models.PositiveIntegerField(choices=(
        (int(OrganizationStatus.ACTIVE), _('Visible')),
        (int(OrganizationStatus.PENDING_DELETION), _('Pending Deletion')),
        (int(OrganizationStatus.DELETION_IN_PROGRESS), _('Deletion in Progress')),
    ), default=int(OrganizationStatus.ACTIVE))
    date_added = models.DateTimeField(default=timezone.now)
    # default_timezone = TimeZoneField()
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='mercury.OrganizationMember')
    billing_email = models.EmailField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='organizations')
    objects = OrganizationManager()

    @classmethod
    def get_default(cls):
        """
        Return the organization used in single organization mode.
        """
        return cls.objects.filter(
            status=OrganizationStatus.VISIBLE,
        ).first()

    def __str__(self):
        return '%s (%s)' % (self.name, self.slug)

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
        if self.is_default:
            raise Exception('You cannot delete the the default organization.')
        return super(Organization, self).delete()

    @cached_property
    def is_default(self):
        if not settings.ON_PREMISE:
            return False

        return self == type(self).get_default()

    def has_access(self, user, access=None):
        queryset = self.members.filter(user=user)
        if access is not None:
            queryset = queryset.filter(type__lte=access)

        return queryset.exists()

    def add_member(self, user, role):
        from mercury.models import OrganizationMember
        return OrganizationMember.objects.get_or_create(organization=self,
                                                        user=user,
                                                        role=int(role))[0]

    def get_owners(self):
        from mercury.models import User
        return User.objects.filter(
            # sentry_orgmember_set__role=roles.get_top_dog().id,
            # sentry_orgmember_set__organization=self,
            is_active=True,
        )

    def get_default_owner(self):
        if not hasattr(self, '_default_owner'):
            self._default_owner = self.get_owners()[0]
        return self._default_owner
