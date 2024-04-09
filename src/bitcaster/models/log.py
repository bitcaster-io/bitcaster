import logging

from django.db import models

from .org import Application

logger = logging.getLogger(__name__)


class LogEntry(models.Model):
    level = models.CharField(max_length=255)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
