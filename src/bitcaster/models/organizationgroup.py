from django.db import models

from bitcaster.models.mixins import ReverseWrapperMixin

from .organization import Organization
from .organizationmember import OrganizationMember


class OrganizationGroup(ReverseWrapperMixin, models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     db_index=True,
                                     related_name='groups')
    members = models.ManyToManyField(OrganizationMember)

    class Meta:
        app_label = 'bitcaster'
        unique_together = (('organization', 'name'),)

    class Reverse:
        pattern = 'org-group-{op}'
        args = ['organization.slug', 'id']

    def __str__(self):
        return str(self.name)
