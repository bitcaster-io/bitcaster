from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from bitcaster.framework.db.fields import DeletionStatusField, Role, RoleField
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
    # members = models.ManyToManyField(User, related_name='teams')
    manager = models.ForeignKey(User,
                                related_name='+',
                                on_delete=models.CASCADE)
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


class ApplicationRole(AbstractModel):
    # application = models.ForeignKey('bitcaster.Application',
    #                                 related_name='application_roles',
    #                                 on_delete=models.CASCADE)
    team = models.ForeignKey(Team,
                             related_name='roles',
                             on_delete=models.CASCADE)
    role = RoleField(default=Role.SUBSCRIBER)

    class Meta:
        unique_together = (('team', 'role'),)
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

    def __str__(self):
        return f'{self.team} {self.get_role_display()}'

    @property
    def members(self):
        return self.team.members
