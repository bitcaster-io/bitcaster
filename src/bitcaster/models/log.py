import logging

from django.db import models
from django.utils.translation import gettext as _

from .application import Application

logger = logging.getLogger(__name__)

LEVELS = zip(logging._nameToLevel.keys(), logging._nameToLevel.keys())


class LogMessage(models.Model):
    level = models.CharField(max_length=255, choices=LEVELS)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Log Message")
        verbose_name_plural = _("Log Messages")
        app_label = "bitcaster"
