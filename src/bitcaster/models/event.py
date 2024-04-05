from uuid import uuid4

from django.db import models

from .org import Application


class EventType(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    description = models.CharField(max_length=255)
    code = models.UUIDField(unique=True, default=uuid4)
