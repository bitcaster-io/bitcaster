from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .organization import Organization, OrganizationRole


class OrganizationMember(models.Model):
    """
    Identifies relationships between teams and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """
    __core__ = True

    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='memberships')
    email = models.EmailField(null=True, blank=True)

    role = models.IntegerField(
        choices=((int(OrganizationRole.OWNER), _('Owner')),
                 (int(OrganizationRole.ADMIN), _('Admin')),
                 (int(OrganizationRole.MEMBER), _('Member')),
                 (int(OrganizationRole.RECIPIENT), _('Recipient')),
                 ),
        default=int(OrganizationRole.RECIPIENT),
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
