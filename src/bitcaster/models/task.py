import uuid
from collections.abc import Iterable
from typing import Any

from apscheduler.triggers.cron import CronTrigger
from cron_descriptor import Options
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.db.models.base import ModelBase

from bitcaster.models.mixins import BitcasterBaseModel, BitcasterBaselManager


class TaskManager(BitcasterBaselManager["Task"]):
    def get_by_natural_key(self, slug: str) -> "Task":
        return self.get(slug=slug)


class Task(BitcasterBaseModel):
    class TriggerOption(models.TextChoices):
        INTERVAL = "interval", "Interval"
        CRON = "cron", "Cron"

    last_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200, unique=True)

    func = models.CharField(max_length=500)
    replace_existing = models.BooleanField(default=False)
    max_instances = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    next_run_time = models.DateTimeField(null=True, blank=True)
    args = JSONField(default=list, blank=True)
    kwargs = JSONField(default=dict, blank=True)

    trigger = models.CharField(max_length=500, choices=TriggerOption.choices, default=TriggerOption.INTERVAL)
    trigger_config = JSONField(default=dict, blank=True)

    active = models.BooleanField(default=False)

    objects = TaskManager()

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

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
