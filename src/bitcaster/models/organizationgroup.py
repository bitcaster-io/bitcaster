from django.db import models
from django.utils.translation import gettext_lazy as _

from bitcaster.models.mixins import ReverseWrapperMixin

from .organization import Organization
from .organizationmember import OrganizationMember


class OrganizationGroup(ReverseWrapperMixin, models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     db_index=True,
                                     related_name='groups')
    members = models.ManyToManyField(OrganizationMember, blank=True)
    closed = models.BooleanField(default=True)

    class Meta:
        app_label = 'bitcaster'
        unique_together = (('organization', 'name'),)
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    class Reverse:
        pattern = 'org-group-{op}'
        args = ['organization.slug', 'id']

    def __str__(self):
        return str(self.name)
