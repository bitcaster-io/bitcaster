from typing import TYPE_CHECKING, Any

from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.admin.models import LogEntry as _LogEntry
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import bitcaster

if TYPE_CHECKING:
    from django.db import Model


class LogEntryManager(_LogEntry.objects.__class__):  # type: ignore[name-defined]
    def get_by_natural_key(self, pk: "str", *args: Any) -> "LogEntry":
        return self.get(pk=pk)

    def log_system_action(self, obj: "Model", action_flag: int, change_message: str = "") -> None:
        user_id = bitcaster.system_user_id
        self.log_actions(user_id=user_id, queryset=[obj], action_flag=action_flag, change_message=change_message)


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
    objects = LogEntryManager()

    class Meta:
        proxy = True
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
            return _("”%(object)s”.") % {"object": self.object_repr}
        return super().__str__()

    def is_other(self) -> bool:
        return self.action_flag == LogEntry.OTHER
