from typing import TYPE_CHECKING, Any, Mapping

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from ..constants import AddressType
from ..dispatchers.base import MessageProtocol
from ..utils.address import is_email, is_phonenumber
from .mixins import BitcasterBaseModel, BitcasterBaselManager
from .user import User

if TYPE_CHECKING:
    from .assignment import Assignment
    from .channel import Channel


class AddressManager(BitcasterBaselManager["Address"]):
    use_for_related_fields = True

    def get_or_create(self, defaults: Mapping[str, Any] | None = None, **kwargs: Any) -> "tuple[Address, bool]":
        kwargs["type"] = self.get_type_from_value(kwargs.get("value", ""))
        return super().get_or_create(defaults=defaults, **kwargs)

    def valid(self) -> QuerySet["Address"]:
        # FIXME: Notification works also if assignment is not validated, this method is never used
        return self.filter(assignments__validated=True)

    def get_by_natural_key(self, user: str, name: str) -> "Address":
        return self.get(user__username=user, name=name)

    def get_type_from_value(self, value: str) -> AddressType:
        if is_phonenumber(value):
            return AddressType.PHONE
        if is_email(value):
            return AddressType.EMAIL
        return AddressType.GENERIC


PROTOCOL_TO_ADDRESS = {
    MessageProtocol.PLAINTEXT: AddressType.GENERIC,
    MessageProtocol.EMAIL: AddressType.EMAIL,
    MessageProtocol.SMS: AddressType.PHONE,
    MessageProtocol.SLACK: AddressType.ACCOUNT,
    MessageProtocol.WEBPUSH: AddressType.EMAIL,
}


class Address(BitcasterBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=255, help_text="Label or mnemonic name for this address")
    type = models.CharField(
        max_length=10, choices=AddressType.choices, default=AddressType.GENERIC, help_text="Type of address"
    )
    value = models.CharField(max_length=255, help_text="Specific address value.")
    assignments: "QuerySet[Assignment]"

    objects = AddressManager()

    class Meta:
        unique_together = (("user", "name"), ("user", "value"))
        ordering = ("name",)

    def __str__(self) -> str:
        return self.value

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.type = Address.objects.get_type_from_value(self.value)
        super().save(*args, **kwargs)

    def natural_key(self) -> tuple[str, str]:
        return self.user.username, self.name

    @cached_property
    def channels(self) -> "QuerySet[Channel]":
        from .channel import Channel

        return Channel.objects.filter(assignments__address=self)

    def validate_channel(self, ch: "Channel") -> "Assignment":
        return self.assignments.update_or_create(channel=ch, defaults={"validated": True})[0]
