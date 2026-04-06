import logging
from typing import TYPE_CHECKING

from django.contrib.admin import SimpleListFilter

from bitcaster.admin.base import BaseAdmin

from .base import BitcasterModelAdmin

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.admin import ModelAdmin
    from django.db.models import QuerySet
    from django.http import HttpRequest

    from bitcaster.models import Channel, ProcessLogEntry

logger = logging.getLogger(__name__)


class TaskFilter(SimpleListFilter):
    parameter_name = "type"
    title = "Type"

    def lookups(self, request: "HttpRequest", model_admin: "ModelAdmin[Channel]") -> tuple[tuple[str, str], ...]:
        return self.prefixes

    def queryset(self, request: "HttpRequest", queryset: "QuerySet[Channel]") -> "QuerySet[Channel]":
        if self.value() == "abstract":
            return queryset.filter(organization__isnull=False, project__isnull=True)
        if self.value() == "project":
            return queryset.filter(organization__isnull=False, project__isnull=False)
        return queryset.all()


class ProcessLogEntryAdmin(BaseAdmin, BitcasterModelAdmin["ProcessLogEntry"]):
    search_fields = ("task_name",)
    list_display = ("action_time", "status", "elapsed", "task_name")
    list_filter = (
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
