import json
from typing import Any, Iterable

from django.db import models
from django.utils.translation import gettext as _
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from strategy_field.fields import StrategyField

from bitcaster.agents.base import Agent, agentManager
from bitcaster.models.mixins import AdminReversable, BaseQuerySet, BitcasterBaselManager


class MonitorQuerySet(BaseQuerySet["Monitor"]):
    def get_by_natural_key(self, name: str, *args: Any) -> "Monitor":
        return self.get(name=name)


class MonitorManager(BitcasterBaselManager.from_queryset(MonitorQuerySet)):
    _queryset_class = MonitorQuerySet


class Monitor(AdminReversable, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    event = models.ForeignKey("Event", related_name="%(class)s_set", on_delete=models.CASCADE, blank=False)
    agent: "Agent" = StrategyField(registry=agentManager)
    active = models.BooleanField(default=True)
    config = models.JSONField(blank=True, default=dict, editable=False)
    data = models.JSONField(blank=True, default=dict, editable=False)
    result = models.JSONField(blank=True, default=dict, editable=False)
    async_result = models.CharField(blank=True, default="", editable=False, max_length=255)

    schedule = models.ForeignKey(
        PeriodicTask,
        verbose_name=_("Scheduling"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="monitors",
    )

    objects = MonitorManager()

    def __str__(self) -> str:
        return self.name

    def save(  # type: ignore[override]
        self,
        *args: Any,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        super().save(
            *args, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields
        )
        if self.schedule is None:
            every_hour, _ = CrontabSchedule.objects.get_or_create(hour="*/1")
            pt, __ = PeriodicTask.objects.get_or_create(
                name=self.name,
                task="bitcaster.tasks.monitor_run",
                kwargs=json.dumps({"pk": self.pk}),
                defaults={"crontab": every_hour},
            )
            self.schedule = pt
            self.save()

    def natural_key(self) -> tuple[str | None, ...]:
        return (self.name,)

    def has_changes(self) -> bool:
        return self.agent.changes_detected()
