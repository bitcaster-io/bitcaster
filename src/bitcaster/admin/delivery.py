from typing import cast

from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Delivery

from .base import BaseAdmin


class DeliveryAdmin(BaseAdmin[Delivery]):
    list_display = ("pk", "occurrence", "assignment", "notification", "channel", "status", "errors")
    list_select_related = (
        "occurrence__event",
        "assignment__address__user",
        "assignment__channel",
        "notification",
        "channel",
        "message_template",
    )
    ordering = ("-id",)

    def get_list_display(self, request: HttpRequest) -> list[str]:  # type: ignore[override]
        return cast("list[str]", super().get_list_display(request))

    def get_queryset(self, request: HttpRequest) -> QuerySet[Delivery]:
        return super().get_queryset(request).select_related(*self.list_select_related)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Delivery | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Delivery | None = None) -> bool:
        return False
