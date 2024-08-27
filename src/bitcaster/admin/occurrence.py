import logging
from typing import Optional

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.numbers import NumberFilter
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _

from bitcaster.models import Occurrence
from bitcaster.tasks import purge_occurrences

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
        html_attrs={"style": f"background-color:{ButtonColor.ACTION.value}"},
        visible=lambda btn: btn.original.status == btn.original.Status.NEW,
    )
    def process(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj = self.get_object(request, pk)
        obj.process()

    @button(
        html_attrs={"style": f"background-color:{ButtonColor.ACTION}"},
        permission="bitcaster.delete_occurrence",
    )
    def purge(self, request: HttpRequest) -> HttpResponse:  # noqa
        purge_occurrences.delay()
        self.message_user(request, _("Occurrence purge has been successfully triggered"), messages.INFO)
