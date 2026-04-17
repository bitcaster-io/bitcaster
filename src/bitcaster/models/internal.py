import logging
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

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
    level = models.CharField(verbose_name=_("Level"), max_length=255, choices=LEVELS, help_text=_("Log message level"))
    message = models.TextField(verbose_name=_("Message"), help_text=_("message body"))
    created = models.DateTimeField(verbose_name=_("Date"), auto_now_add=True, help_text=_("date of this message"))
    application = models.ForeignKey(
        Application,
        verbose_name=_("Application"),
        on_delete=models.CASCADE,
        help_text=_("application linked to this message"),
    )

    objects = LogMessageManager()

    class Meta:
        verbose_name = _("Log Message")
        verbose_name_plural = _("Log Messages")
        app_label = "bitcaster"

    def natural_key(self) -> tuple[str | None, ...]:
        return str(self.created), *self.application.natural_key()
