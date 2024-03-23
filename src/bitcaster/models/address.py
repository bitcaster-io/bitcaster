from .auth import User
from django.db import models


class Address(models.Model):
    value = models.CharField(max_length=255, db_collation="case_insensitive")
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.value
