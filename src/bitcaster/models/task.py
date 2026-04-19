import uuid
from collections.abc import Iterable
from typing import Any

from apscheduler.triggers.cron import CronTrigger
from cron_descriptor import Options
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.db.models.base import ModelBase
from django.utils.translation import gettext_lazy as _

from bitcaster.models.mixins import BitcasterBaseModel, BitcasterBaselManager


class TaskManager(BitcasterBaselManager["Task"]):
    def get_by_natural_key(self, slug: str) -> "Task":
        return self.get(slug=slug)


def get_tasks() -> list[tuple[str, str]]:
    from bitcaster.runner.config import SCHEDULER

    return sorted([(entry["func"], entry["func"]) for entry in SCHEDULER.values()])


class Task(BitcasterBaseModel):
    class TriggerOption(models.TextChoices):
        INTERVAL = "interval", _("Interval")
        CRON = "cron", _("Cron")

    last_updated = models.DateTimeField(verbose_name=_("Last updated"), auto_now=True, help_text=_("Last updated"))
    slug = models.SlugField(verbose_name=_("Slug"), unique=True, help_text=_("Slug"))
    name = models.CharField(verbose_name=_("Name"), max_length=200, unique=True, help_text=_("Name"))

    func = models.CharField(
        verbose_name=_("Func"),
        max_length=500,
        choices=get_tasks,
        help_text=_("Func"),
    )
    replace_existing = models.BooleanField(
        verbose_name=_("Replace existing"), default=False, help_text=_("Replace existing")
    )
    max_instances = models.IntegerField(
        verbose_name=_("Max instances"), default=1, validators=[MinValueValidator(1)], help_text=_("Max instances")
    )
    next_run_time = models.DateTimeField(
        verbose_name=_("Next run time"), blank=True, null=True, help_text=_("Next run time")
    )
    args = JSONField(verbose_name=_("Args"), blank=True, default=list, help_text=_("Args"))
    kwargs = JSONField(verbose_name=_("Kwargs"), blank=True, default=dict, help_text=_("Kwargs"))

    trigger = models.CharField(
        verbose_name=_("Trigger"),
        max_length=500,
        choices=TriggerOption.choices,
        default=TriggerOption.INTERVAL,
        help_text=_("Trigger"),
    )
    trigger_config = JSONField(
        verbose_name=_("Trigger config"), blank=True, default=dict, help_text=_("Trigger config")
    )

    active = models.BooleanField(verbose_name=_("Active"), default=False, help_text=_("Active"))

    objects = TaskManager()

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def __str__(self) -> str:
        return self.name

    def scheduling(self) -> str:
        if self.trigger == Task.TriggerOption.INTERVAL:
            parts = []
            for unit in ["weeks", "days", "hours", "minutes", "seconds"]:
                value = self.trigger_config.get(unit)
                if value:
                    label = unit
                    if value == 1:
                        label = unit[:-1]
                    parts.append(f"{value} {label}")
            return f"Every {', '.join(parts)}"

        if self.trigger == Task.TriggerOption.CRON:
            try:
                from cron_descriptor import get_description

                cron_expression = "{minute} {hour} {day} {month} {day_of_week}".format(
                    minute=self.trigger_config.get("minute", "*"),
                    hour=self.trigger_config.get("hour", "*"),
                    day=self.trigger_config.get("day", "*"),
                    month=self.trigger_config.get("month", "*"),
                    day_of_week=self.trigger_config.get("day_of_week", "*"),
                )
                options: Options = Options(locale_code="en_US", use_24hour_time_format=False)
                return get_description(cron_expression, options)
            except ImportError:
                return str(CronTrigger(**self.trigger_config))
        return "Invalid trigger type"

    def get_job_args(self) -> dict[str, Any]:
        return {
            "id": self.slug,
            "func": self.func,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "next_run_time": self.next_run_time,
            "trigger": self.trigger,
            **self.trigger_config,
        }

    def save(
        self,
        *,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        if not self.slug:
            self.slug = uuid.uuid4().hex
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def natural_key(self) -> tuple[str, ...]:
        return (self.slug,)

    def get_status(self) -> str:
        if self.active:
            return "active"
        return "paused"
