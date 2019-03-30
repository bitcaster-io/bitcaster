from django.conf import settings
from django.db import models

from bitcaster.framework.db.fields import RoleField

from .application import Application
from .organizationmember import OrganizationMember


class ApplicationMember(models.Model):
    """
    Identifies relationships between teams and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """

    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    db_index=True,
                                    related_name='memberships')
    org_member = models.ForeignKey(OrganizationMember,
                                   db_index=True,
                                   on_delete=models.CASCADE,
                                   related_name='application')
    # this is a denormalization
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             db_index=True,
                             on_delete=models.CASCADE,
                             related_name='application')
    role = RoleField()

    class Meta:
        app_label = 'bitcaster'
        unique_together = (
            ('application', 'org_member'),
        )

    def __str__(self):
        return str(self.user)
