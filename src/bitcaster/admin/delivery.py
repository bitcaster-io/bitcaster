from typing import Any, cast

from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Delivery, Occurrence

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
    list_filter = ("occurrence__event",)
    search_fields = ("assignment__address__user__email", "assignment__address__value")
    ordering = ("-id",)

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        extra_context = extra_context or {}
        occurrence_id = request.GET.get("occurrence__exact")
        if occurrence_id:
            try:
                occurrence = Occurrence.objects.select_related("event").get(pk=occurrence_id)
                url = reverse("admin:bitcaster_occurrence_change", args=[occurrence.pk])
                extra_context["subtitle"] = format_html(
                    _('Deliveries for <a href="{url}">{occurrence}</a>'), url=url, occurrence=occurrence
                )
            except (Occurrence.DoesNotExist, ValueError):
                pass
        return super().changelist_view(request, extra_context=extra_context)

    def get_fields(self, request: HttpRequest, obj: Delivery | None = None) -> list[str]:  # type: ignore[override]
        fields = list(super().get_fields(request, obj))
        if not request.user.has_perm("bitcaster.read_data_delivery"):
            fields = [f for f in fields if f != "data"]
        return fields

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
