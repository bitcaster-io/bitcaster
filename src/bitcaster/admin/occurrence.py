import logging
from typing import Optional

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.numbers import NumberFilter
from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from bitcaster.models import Occurrence

from .base import BaseAdmin, ButtonColor

logger = logging.getLogger(__name__)


class OccurrenceAdmin(BaseAdmin, admin.ModelAdmin[Occurrence]):
    search_fields = ("name",)
    list_display = ("timestamp", "event", "status", "attempts", "recipients")
    list_filter = (
        "timestamp",
        ("event", AutoCompleteFilter),
        "status",
        ("recipients", NumberFilter),
    )
    readonly_fields = ["correlation_id"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[Occurrence] = None) -> bool:
        return False

    @button(
        html_attrs={"style": f"background-color:{ButtonColor.ACTION}"},
        visible=lambda btn: btn.original.status == btn.original.Status.NEW,
    )
    def process(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj = self.get_object(request, pk)
        obj.process()
