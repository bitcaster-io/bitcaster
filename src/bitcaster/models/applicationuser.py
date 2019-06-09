from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.framework.db.fields import ApplicationRoleField
from bitcaster.models.mixins import ReverseWrapperMixin

from .application import Application
from .organizationmember import OrganizationMember


class ApplicationUser(ReverseWrapperMixin, models.Model):
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    db_index=True,
                                    related_name='memberships')
    org_member = models.ForeignKey(OrganizationMember,
                                   db_index=True,
                                   on_delete=models.CASCADE,
                                   related_name='applications')
    role = ApplicationRoleField()

    class Meta:
        app_label = 'bitcaster'
        verbose_name = _('Application Member')
        verbose_name_plural = _('Application Members')
        unique_together = (
            ('application', 'org_member'),
        )

    class Reverse:
        pattern = 'app-member-{op}'
        args = ['application.organization.slug', 'application.slug', 'id']

    @cached_property
    def user(self):
        return self.org_member.user

    def __str__(self):
        return str(self.org_member.user)
