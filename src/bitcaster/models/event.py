from django.db import models


class EventType(models.Model):
    sender = models.ForeignKey("Sender", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    description = models.CharField(max_length=255, db_collation="case_insensitive")
