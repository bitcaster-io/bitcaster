from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from bitcaster.framework.db.fields import DeletionStatusField, RoleField
from bitcaster.utils.slug import slugify_instance

from .base import AbstractModel
from .organizationmember import OrganizationMember
from .user import User


class Team(AbstractModel):
    """
    A team represents a group of individuals belongs same organization
    """
    application = models.ForeignKey('bitcaster.Application',
                                    related_name='teams',
                                    on_delete=models.CASCADE)
    members = models.ManyToManyField(OrganizationMember)
    manager = models.ForeignKey(User,
                                related_name='+',
                                on_delete=models.CASCADE)
    role = RoleField()
    slug = models.SlugField()
    name = models.CharField(_('Name'), max_length=64)
    description = models.CharField(_('Description'), max_length=255, null=True, blank=True)
    status = DeletionStatusField()
    date_added = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        app_label = 'bitcaster'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # lock = locks.get('slug:team', 5)
            # with TimedRetryPolicy(10, lock.acquire):
            slugify_instance(self, self.name, application=self.application)
            super(Team, self).save(*args, **kwargs)
        else:
            super(Team, self).save(*args, **kwargs)
