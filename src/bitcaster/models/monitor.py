from typing import Any, Iterable

from django.db import models
from django.utils.translation import gettext_lazy as _
from strategy_field.fields import StrategyField

from bitcaster.agents.base import Agent, agentManager

from .event import Event
from .mixins import AdminReversable, BaseQuerySet, BitcasterBaselManager


class MonitorQuerySet(BaseQuerySet["Monitor"]):
    def get_by_natural_key(self, name: str, *args: Any) -> "Monitor":
        return self.get(name=name)


class MonitorManager(BitcasterBaselManager.from_queryset(MonitorQuerySet)):
    _queryset_class = MonitorQuerySet


class Monitor(AdminReversable, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255, help_text=_("name for this monitor"))
    event = models.ForeignKey(
        Event, verbose_name=_("Event"), on_delete=models.CASCADE, related_name="%(class)s_set", blank=False
    )
    agent: "Agent" = StrategyField(verbose_name=_("Agent"), registry=agentManager, help_text=_("Agent to use"))
    active = models.BooleanField(verbose_name=_("Active"), default=True, help_text=_("Enable/Disable monitor"))
    config = models.JSONField(
        verbose_name=_("Configuration"), blank=True, default=dict, editable=False, help_text=_("monitor configuration")
    )
    data = models.JSONField(
        verbose_name=_("Data"), blank=True, default=dict, editable=False, help_text=_("monitor daa")
    )
    result = models.JSONField(
        verbose_name=_("Latest result"),
        blank=True,
        default=dict,
        editable=False,
        help_text=_("monitor last execution result"),
    )
    async_result = models.CharField(
        verbose_name=_("async_result"),
        max_length=255,
        blank=True,
        default="",
        editable=False,
        help_text=_("async_result"),
    )

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
