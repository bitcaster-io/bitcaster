"""
sentry.models.organizationmember
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import, print_function

from enum import Enum

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class OrganizationRole(Enum):
    ADMIN = 1
    MEMBER = 2


class OrganizationMember(models.Model):
    """
    Identifies relationships between teams and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """
    __core__ = True

    organization = models.ForeignKey('mercury.Organization',
                                     on_delete=models.CASCADE,
                                     related_name='+')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='+')
    email = models.EmailField(null=True, blank=True)

    role = models.IntegerField(
        choices=((OrganizationRole.ADMIN, 'Admin'),
                 (OrganizationRole.MEMBER, 'Member'),
                 ),
        default=OrganizationRole.MEMBER,
    )

    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (
            ('organization', 'user'),
            ('organization', 'email'),
        )

    @transaction.atomic
    def save(self, *args, **kwargs):
        assert self.user_id or self.email, \
            'Must set user or email'
        super(OrganizationMember, self).save(*args, **kwargs)

    @property
    def is_pending(self):
        return self.user_id is None
