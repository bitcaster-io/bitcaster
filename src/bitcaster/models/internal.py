import logging
from typing import Any

from django.db import models
from django.utils.translation import gettext as _

from .application import Application
from .mixins import BitcasterBaseModel, BitcasterBaselManager

logger = logging.getLogger(__name__)

LEVELS = zip(logging._nameToLevel.keys(), logging._nameToLevel.keys(), strict=False)


class LogMessageManager(BitcasterBaselManager["LogMessage"]):
    def get_by_natural_key(self, created: "str", app: str, prj: str, org: str, *args: Any) -> "LogMessage":
        return self.get(
            created=created,
            application__project__organization__slug=org,
            application__project__slug=prj,
            application__slug=app,
        )


class LogMessage(BitcasterBaseModel):
    level = models.CharField(max_length=255, choices=LEVELS)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    objects = LogMessageManager()

    class Meta:
        verbose_name = _("Log Message")
        verbose_name_plural = _("Log Messages")
        app_label = "bitcaster"

    def natural_key(self) -> tuple[str | None, ...]:
        return str(self.created), *self.application.natural_key()
