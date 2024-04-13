import typing

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from ..constants import AddressType
from .user import User

if typing.TYPE_CHECKING:
    from .channel import Channel


class AddressManager(models.Manager["Address"]):
    def valid(self) -> QuerySet["Address"]:
        return self.filter(validated=True)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    type = models.CharField(max_length=10, choices=AddressType.choices, default=AddressType.GENERIC)
    value = models.CharField(max_length=255)
    validations: "QuerySet[Validation]"

    objects = AddressManager()

    class Meta:
        unique_together = (("user", "name"), ("user", "value"))

    def __str__(self) -> str:
        return self.value

    @cached_property
    def channels(self) -> "QuerySet[Channel]":
        from .channel import Channel

        return Channel.objects.filter(validations__address=self)

    def validate_channel(self, ch: "Channel") -> "Validation":
        return Validation.objects.update_or_create(address=self, channel=ch, defaults={"validated": True})[0]


class Validation(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="validations")
    channel = models.ForeignKey("bitcaster.Channel", on_delete=models.CASCADE, related_name="validations")
    validated = models.BooleanField(default=False)

    class Meta:
        unique_together = (("address", "channel"),)
