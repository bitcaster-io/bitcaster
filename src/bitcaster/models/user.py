import datetime
import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils.crypto import RANDOM_STRING_CHARS
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField

from ..config import settings
from .mixins import BitcasterBaseModel, LockMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from bitcaster.models import Assignment, Channel, DistributionList, Organization

    from .user_message import UserMessageManager

logger = logging.getLogger(__name__)

TOKEN_CHARS = f"{RANDOM_STRING_CHARS}-#@^*_+~;<>,."


class UserManager(BaseUserManager["User"]):
    def get_by_natural_key(self, username: str | None) -> "User":
        return self.get(username=username)


def get_datetime_format_choices() -> list[tuple[str, str]]:
    d = datetime.datetime(2000, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
    options = [f"{x} {y}" for x in settings.DATE_FORMATS for y in settings.TIME_FORMATS]
    return [(e, d.strftime(e)) for e in options]


def get_date_format_choices() -> list[tuple[str, str]]:
    d = datetime.datetime(2000, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
    return [(e, d.strftime(e)) for e in settings.DATE_FORMATS]


def get_time_format_choices() -> list[tuple[str, str]]:
    d = datetime.datetime(2000, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
    return [(e, d.strftime(e)) for e in settings.TIME_FORMATS]


class User(LockMixin, BitcasterBaseModel, AbstractUser):
    timezone = TimeZoneField(default="UTC")

    date_time_format = models.CharField(
        max_length=50, choices=get_datetime_format_choices, default=settings.DATETIME_FORMAT
    )
    date_format = models.CharField(max_length=50, choices=get_date_format_choices, default=settings.DATE_FORMAT)
    time_format = models.CharField(max_length=50, choices=get_time_format_choices, default=settings.TIME_FORMATS)

    custom_fields = models.JSONField(default=dict, blank=True)

    bitcaster_messages: "UserMessageManager"

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        app_label = "bitcaster"
        abstract = False
        permissions = (
            ("console_lock", "Can access Lock console"),
            ("console_tools", "Can access Tools console"),
        )

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

    def format_date(self, d: datetime.datetime) -> str:
        return d.strftime(self.date_format)

    def format_time(self, d: datetime.datetime) -> str:
        return d.strftime(self.time_format)

    def format_datetime(self, d: datetime.datetime) -> str:
        return d.strftime(f"{self.date_format} {self.time_format}")


class Member(User):
    class Meta:
        proxy = True
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
