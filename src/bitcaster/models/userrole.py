import logging
from typing import Any

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext as _

from .mixins import BitcasterBaseModel
from .organization import Organization
from .user import User

logger = logging.getLogger(__name__)


class UserRoleManager(models.Manager["UserRole"]):
    def get_by_natural_key(self, group: str, user: str, org: str, *args: Any) -> "UserRole":
        return self.get(group__name=group, user__username=user, organization__slug=org)


class UserRole(BitcasterBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    objects = UserRoleManager()

    class Meta:
        verbose_name = _("User Role")
        verbose_name_plural = _("User Roles")
        unique_together = (("organization", "user", "group"),)

    def natural_key(self) -> tuple[str | None, ...]:
        return self.group.name, self.user.username, *self.organization.natural_key()
