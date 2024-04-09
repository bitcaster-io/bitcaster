import logging

from django.db import models
from django.utils.translation import gettext as _

from .org import Application

logger = logging.getLogger(__name__)

LEVELS = zip(logging._nameToLevel.keys(), logging._nameToLevel.keys())


class LogEntry(models.Model):
    level = models.CharField(max_length=255, choices=LEVELS)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Log Entry")
        verbose_name_plural = _("Log Entries")
