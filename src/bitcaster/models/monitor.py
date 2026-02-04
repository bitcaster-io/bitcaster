from typing import Any, Iterable

from django.db import models
from django.utils.translation import gettext_lazy as _
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

    objects = MonitorManager()

    class Meta:
        verbose_name = _("Monitor")
        verbose_name_plural = _("Monitors")
        ordering = ("name",)

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

    def natural_key(self) -> tuple[str | None, ...]:
        return (self.name,)

    def has_changes(self) -> bool:
        return self.agent.changes_detected()
