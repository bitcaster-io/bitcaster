import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils.crypto import RANDOM_STRING_CHARS
from django.utils.translation import gettext_lazy as _

from .mixins import BitcasterBaseModel, LockMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from bitcaster.models import Assignment, Channel, DistributionList, Organization

logger = logging.getLogger(__name__)

TOKEN_CHARS = f"{RANDOM_STRING_CHARS}-#@^*_+~;<>,."


class UserManager(BaseUserManager["User"]):
    def get_by_natural_key(self, username: str | None) -> "User":
        return self.get(username=username)


class User(LockMixin, BitcasterBaseModel, AbstractUser):
    custom_fields = models.JSONField(default=dict, blank=True)
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        app_label = "bitcaster"
        abstract = False
        permissions = (("bitcaster.lock_system", "Can lock system components"),)

    @property
    def organizations(self) -> "QuerySet[Organization]":
        from bitcaster.models import Organization

        if self.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(userrole__user=self)

    def natural_key(self) -> tuple[str]:
        return (self.username,)

    def get_assignment_for_channel(self, ch: "Channel") -> "Assignment | None":
        from bitcaster.models import Assignment

        return Assignment.objects.filter(address__user=self, channel=ch).first()

    @property
    def distribution_lists(self) -> "QuerySet[DistributionList]":
        """Retrieve all distribution lists this user is a recipient of via any assignment."""
        from bitcaster.models import DistributionList

        return DistributionList.objects.filter(recipients__address__user=self)
