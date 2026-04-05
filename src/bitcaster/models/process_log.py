from collections.abc import Callable
from typing import Any

from django.contrib.admin.models import LogEntry as _LogEntry
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from bitcaster.utils.json import safe_dumps


class LogEntryManager(_LogEntry.objects.__class__):  # type: ignore[name-defined]
    def get_by_natural_key(self, pk: "str", *args: Any) -> "ProcessLogEntry":
        return self.get(pk=pk)

    def log_process(
        self,
        fn: Callable[[Any], Any],
        elapsed: int | None = None,
        args: Any | None = None,
        error: BaseException | None = None,
        kwargs: Any | None = None,
    ) -> None:
        ProcessLogEntry.objects.create(
            status=ProcessLogEntry.FAILURE if error else ProcessLogEntry.SUCCESS,
            elapsed=elapsed,
            task_name=fn.__name__,
            task_func=fqn(fn),
            exc_info=str(error) if error else "",
            args=safe_dumps(args),
            kwargs=safe_dumps(kwargs),
        )


class ProcessLogEntry(models.Model):
    SUCCESS = 10
    FAILURE = 20
    STATUD_CHOICES = [
        (SUCCESS, _("Success")),
        (FAILURE, _("Failure")),
    ]
    action_time = models.DateTimeField(_("action time"), default=timezone.now, editable=False)
    status = models.IntegerField(_("status"), choices=STATUD_CHOICES, default=SUCCESS)
    elapsed = models.IntegerField(_("elapsed"), blank=True, null=True)
    task_name = models.CharField(max_length=100, null=True, blank=True)
    task_func = models.CharField(max_length=500, null=True, blank=True)
    args = models.JSONField(null=True, blank=True)
    kwargs = models.JSONField(null=True, blank=True)
    exc_info = models.TextField(null=True, blank=True, default="")
    objects = LogEntryManager()

    class Meta:
        app_label = "bitcaster"
        verbose_name = _("process log entry")
        verbose_name_plural = _("process log entries")

    def __str__(self) -> str:
        return str(self.task_name)

    def natural_key(self) -> tuple[str | None, ...]:
        return (str(self.pk),)
