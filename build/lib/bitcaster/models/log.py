from typing import Any

from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.admin.models import LogEntry as _LogEntry
from django.utils.translation import gettext
from django.utils.translation import gettext as _

from bitcaster.models.mixins import BitcasterBaselManager


class LogEntryManager(BitcasterBaselManager["LogEntry"]):
    def get_by_natural_key(self, pk: "str", *args: Any) -> "LogEntry":
        return self.get(pk=pk)


class LogEntry(_LogEntry):
    ADDITION = ADDITION
    CHANGE = CHANGE
    DELETION = DELETION
    OTHER = 100
    ACTION_FLAG_CHOICES = [
        (ADDITION, _("Addition")),
        (CHANGE, _("Change")),
        (DELETION, _("Deletion")),
        (OTHER, _("Other")),
    ]
    objects = LogEntryManager()  # type: ignore

    class Meta:
        app_label = "bitcaster"
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")

    def natural_key(self) -> tuple[str | None, ...]:
        return (str(self.pk),)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._meta.get_field("action_flag").choices = self.ACTION_FLAG_CHOICES

    def __str__(self) -> str:
        if self.is_other():
            return gettext("”%(object)s”.") % {"object": self.object_repr}
        return super().__str__()

    def is_other(self) -> bool:
        return self.action_flag == LogEntry.OTHER
