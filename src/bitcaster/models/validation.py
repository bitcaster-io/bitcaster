from django.db import models


class Validation(models.Model):
    address = models.ForeignKey("bitcaster.Address", on_delete=models.CASCADE, related_name="validations")
    channel = models.ForeignKey("bitcaster.Channel", on_delete=models.CASCADE, related_name="validations")
    validated = models.BooleanField(default=False)

    class Meta:
        unique_together = (("address", "channel"),)

    def __str__(self) -> str:
        return f"{self.address} - {self.channel}"
