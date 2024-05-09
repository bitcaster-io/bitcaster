import typing

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from ..constants import AddressType
from .mixins import BitcasterBaselManager, BitcasterBaseModel
from .user import User

if typing.TYPE_CHECKING:
    from .channel import Channel
    from .validation import Validation


class AddressManager(BitcasterBaselManager["Address"]):
    def valid(self) -> QuerySet["Address"]:
        return self.filter(validations__validated=True)

    def get_by_natural_key(self, user: str, name: str) -> "Address":
        return self.get(user__username=user, name=name)


class Address(BitcasterBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    type = models.CharField(max_length=10, choices=AddressType.choices, default=AddressType.GENERIC)
    value = models.CharField(max_length=255)
    validations: "QuerySet[Validation]"

    objects = AddressManager()

    class Meta:
        unique_together = (("user", "name"), ("user", "value"))
        ordering = ("name",)

    def __str__(self) -> str:
        return self.value

    def natural_key(self) -> tuple[str, str]:
        return self.user.username, self.name

    @cached_property
    def channels(self) -> "QuerySet[Channel]":
        from .channel import Channel

        return Channel.objects.filter(validations__address=self)

    def validate_channel(self, ch: "Channel") -> "Validation":
        return self.validations.update_or_create(channel=ch, defaults={"validated": True})[0]
