import logging
from typing import TYPE_CHECKING

from django.contrib.admin import SimpleListFilter
from strategy_field.utils import fqn

from bitcaster.admin.base import BaseAdmin

from ..runner.manager import BackgroundManager
from .base import BitcasterModelAdmin

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.admin import ModelAdmin
    from django.db.models import QuerySet
    from django.http import HttpRequest

    from bitcaster.models import ProcessLogEntry

logger = logging.getLogger(__name__)


class TaskFilter(SimpleListFilter):
    parameter_name = "task_func"
    title = "Type"

    def lookups(self, request: "HttpRequest", model_admin: "ModelAdmin[ProcessLogEntry]") -> list[tuple[str, str]]:
        return sorted(
            [
                (fqn(actor.fn), actor.actor_name)
                for actor in BackgroundManager().actors
                if actor.options.get("logging", False)
            ]
        )

    def queryset(self, request: "HttpRequest", queryset: "QuerySet[ProcessLogEntry]") -> "QuerySet[ProcessLogEntry]":
        if self.value():
            return queryset.filter(task_func=self.value())
        return queryset.all()


class ProcessLogEntryAdmin(BaseAdmin, BitcasterModelAdmin["ProcessLogEntry"]):
    search_fields = ("task_name",)
    list_display = ("action_time", "status", "elapsed", "task_name")
    list_filter = (
        TaskFilter,
        "action_time",
        "status",
    )
    readonly_fields = ("exc_info",)

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return False

    def has_change_permission(self, request: "HttpRequest", obj: "ProcessLogEntry | None" = None) -> bool:
        return False

    def has_delete_permission(self, request: "HttpRequest", obj: "ProcessLogEntry | None" = None) -> bool:
        return False

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[ProcessLogEntry]":
        return super().get_queryset(request)
