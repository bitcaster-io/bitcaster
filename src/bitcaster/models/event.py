from django.db import models

from .org import Application


class EventType(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
