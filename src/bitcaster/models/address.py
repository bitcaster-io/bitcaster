from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from ..constants import AddressType
from ..dispatchers.base import MessageProtocol
from ..utils.address import is_email, is_phonenumber
from .mixins import BitcasterBaselManager, BitcasterBaseModel
from .user import User

if TYPE_CHECKING:
    from .assignment import Assignment
    from .channel import Channel


class AddressManager(BitcasterBaselManager["Address"]):
    use_for_related_fields = True

    def valid(self) -> QuerySet["Address"]:
        return self.filter(assignments__validated=True)

    def get_by_natural_key(self, user: str, name: str) -> "Address":
        return self.get(user__username=user, name=name)


PROTOCOL_TO_ADDRESS = {
    MessageProtocol.PLAINTEXT: AddressType.GENERIC,
    MessageProtocol.EMAIL: AddressType.EMAIL,
    MessageProtocol.SMS: AddressType.PHONE,
    MessageProtocol.SLACK: AddressType.ACCOUNT,
    MessageProtocol.WEBPUSH: AddressType.EMAIL,
}


class Address(BitcasterBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=AddressType.choices, default=AddressType.GENERIC)
    value = models.CharField(max_length=255)
    assignments: "QuerySet[Assignment]"

    objects = AddressManager()

    class Meta:
        unique_together = (("user", "name"), ("user", "value"))
        ordering = ("name",)

    def __str__(self) -> str:
        return self.value

    def save(self, *args: Any, **kwargs: Any) -> None:
        if is_phonenumber(self.value):
            self.type = AddressType.PHONE
        if is_email(self.value):
            self.type = AddressType.EMAIL
        else:
            self.type = AddressType.ACCOUNT
        super().save(*args, **kwargs)

    def natural_key(self) -> tuple[str, str]:
        return self.user.username, self.name

    @cached_property
    def channels(self) -> "QuerySet[Channel]":
        from .channel import Channel

        return Channel.objects.filter(assignments__address=self)

    def validate_channel(self, ch: "Channel") -> "Assignment":
        return self.assignments.update_or_create(channel=ch, defaults={"validated": True})[0]
