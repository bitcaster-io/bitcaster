from typing import TYPE_CHECKING, Any

from django.contrib.admin.models import LogEntry as _LogEntry
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster.utils.json import safe_dumps

if TYPE_CHECKING:
    from dramatiq import Actor

    from django.utils.functional import _StrPromise


def mask_secrets(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            k: ("********" if any(s in k.lower() for s in ["password", "secret", "token", "key"]) else mask_secrets(v))
            for k, v in data.items()
        }
    if isinstance(data, list | tuple):
        return [mask_secrets(v) for v in data]
    return data


class LogEntryManager(_LogEntry.objects.__class__):  # type: ignore[name-defined]
    def get_by_natural_key(self, pk: "str", *args: Any) -> "ProcessLogEntry":
        return self.get(pk=pk)

    def log_process(
        self,
        actor: "Actor[Any, Any]",
        elapsed: int | None = None,
        args: Any | None = None,
        error: BaseException | None = None,
        kwargs: Any | None = None,
    ) -> None:
        ProcessLogEntry.objects.create(
            status=ProcessLogEntry.FAILURE if error else ProcessLogEntry.SUCCESS,
            elapsed=elapsed,
            task_name=actor.fn.__name__,
            task_func=fqn(actor.fn),
            exc_info=str(error) if error else "",
            args=safe_dumps(mask_secrets(args)),
            kwargs=safe_dumps(mask_secrets(kwargs)),
        )


def _get_status_choices() -> "list[tuple[int, _StrPromise]]":
    return ProcessLogEntry.STATUD_CHOICES


class ProcessLogEntry(models.Model):
    SUCCESS = 10
    FAILURE = 20
    STATUD_CHOICES = [
        (SUCCESS, _("Success")),
        (FAILURE, _("Failure")),
    ]
    action_time = models.DateTimeField(
        verbose_name=_("action time"), default=timezone.now, editable=False, help_text=_("Action time")
    )
    status = models.IntegerField(
        verbose_name=_("status"), choices=_get_status_choices, default=SUCCESS, help_text=_("Status")
    )
    elapsed = models.IntegerField(verbose_name=_("elapsed"), blank=True, null=True, help_text=_("Elapsed time"))
    task_name = models.CharField(
        verbose_name=_("task name"), max_length=100, blank=True, null=True, help_text=_("Task name")
    )
    task_func = models.CharField(
        verbose_name=_("task func"), max_length=500, blank=True, null=True, help_text=_("Task full path")
    )
    args = models.JSONField(verbose_name=_("args"), blank=True, null=True, help_text=_("Task arguments"))
    kwargs = models.JSONField(verbose_name=_("kwargs"), blank=True, null=True, help_text=_("Task keyword arguments"))
    exc_info = models.TextField(
        verbose_name=_("Exc Info"), blank=True, null=True, default="", help_text=_("Exception info")
    )
    objects = LogEntryManager()

    class Meta:
        app_label = "bitcaster"
        verbose_name = _("process log entry")
        verbose_name_plural = _("process log entries")

    def __str__(self) -> str:
        return str(self.task_name)

    def natural_key(self) -> tuple[str | None, ...]:
        return (str(self.pk),)
