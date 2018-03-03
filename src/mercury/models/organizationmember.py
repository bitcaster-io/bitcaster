from __future__ import absolute_import, print_function

from enum import Enum

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class OrganizationRole(Enum):
    OWNER = 99
    ADMIN = 90
    MEMBER = 50

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value


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
        choices=((int(OrganizationRole.OWNER), 'Owner'),
                 (int(OrganizationRole.ADMIN), 'Admin'),
                 (int(OrganizationRole.MEMBER), 'Member'),
                 ),
        default=int(OrganizationRole.MEMBER),
    )

    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (
            ('organization', 'user'),
            ('organization', 'email'),
        )

    def __str__(self):
        return f"{self.organization} {self.user}/{self.role}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        assert self.user_id or self.email, \
            'Must set user or email'
        super(OrganizationMember, self).save(*args, **kwargs)

    @property
    def is_pending(self):
        return self.user_id is None
