from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.framework.db.fields import OrganizationRoleField

from .organization import Organization


class OrganizationMember(models.Model):
    """
    Identifies relationships between teams and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """

    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     db_index=True,
                                     related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             db_index=True,
                             on_delete=models.CASCADE,
                             related_name='memberships')
    role = OrganizationRoleField()
    date_enrolled = models.DateTimeField(default=timezone.now, help_text='enrollemnt date')

    class Meta:
        app_label = 'bitcaster'
        unique_together = (
            ('organization', 'user'),
        )
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    def __str__(self):
        return str(self.user)
