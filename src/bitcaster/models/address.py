from django.db import models

from .auth import User


class AddressManager(models.Manager):
    def valid(self):
        return self.filter(validated=True)


class Address(models.Model):
    value = models.CharField(max_length=255, db_collation="case_insensitive")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE)
    validated = models.BooleanField(default=False)

    objects = AddressManager()

    def __str__(self) -> str:
        return self.value
