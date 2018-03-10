from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from bitcaster.db.fields import DeletionStatusField, Role, RoleField
from bitcaster.utils import locks
from bitcaster.utils.retries import TimedRetryPolicy
from bitcaster.utils.slug import slugify_instance

from .base import AbstractModel
from .organization import Organization
from .user import User


class Team(AbstractModel):
    """
    A team represents a group of individuals which maintain ownership of projects.
    """
    organization = models.ForeignKey(Organization,
                                     related_name='teams',
                                     on_delete=models.CASCADE)
    members = models.ManyToManyField(User,
                                     related_name='teams',
                                     through='bitcaster.TeamMembership')
    manager = models.ForeignKey(User,
                                related_name='+',
                                on_delete=models.CASCADE)
    slug = models.SlugField()
    name = models.CharField(_("Name"), max_length=64)
    status = DeletionStatusField()
    date_added = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        unique_together = (('organization', 'slug'),)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            lock = locks.get('slug:team', duration=5)
            with TimedRetryPolicy(10, lock.acquire):
                slugify_instance(self, self.name, organization=self.organization)
            super(Team, self).save(*args, **kwargs)
        else:
            super(Team, self).save(*args, **kwargs)


class TeamMembership(AbstractModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE,
                             related_name='memberships')
    member = models.ForeignKey(User, on_delete=models.CASCADE)


class ApplicationTeam(AbstractModel):
    application = models.ForeignKey('bitcaster.Application',
                                    on_delete=models.CASCADE)
    team = models.ForeignKey('bitcaster.Team',
                             on_delete=models.CASCADE)
    role = RoleField(default=Role.RECIPIENT)

    class Meta:
        unique_together = (('application', 'team'),)
