from typing import cast

from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import DeliverySimulation

from .base import BaseAdmin


class DeliverySimulationAdmin(BaseAdmin[DeliverySimulation]):
    list_display = ("pk", "simulation", "assignment", "notification", "message_template", "status")
    list_select_related = (
        "simulation__event",
        "assignment__address__user",
        "assignment__channel",
        "notification",
        "message_template",
    )
    ordering = ("-simulation__timestamp",)

    def get_list_display(self, request: HttpRequest) -> list[str]:  # type: ignore[override]
        return cast("list[str]", super().get_list_display(request))

    def get_queryset(self, request: HttpRequest) -> QuerySet[DeliverySimulation]:
        return super().get_queryset(request).select_related(*self.list_select_related)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: DeliverySimulation | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: DeliverySimulation | None = None) -> bool:
        return False
