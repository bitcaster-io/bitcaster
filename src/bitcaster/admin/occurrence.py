import logging

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.filters import NumberFilter
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.forms.widgets import Media
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from bitcaster.models import Occurrence
from bitcaster.tasks import purge_occurrences

from .base import BaseAdmin, ButtonColor

logger = logging.getLogger(__name__)


class OccurrenceAdmin(BaseAdmin, admin.ModelAdmin[Occurrence]):
    search_fields = ("name",)
    list_display = ("timestamp", "application", "event", "status", "attempts", "recipients")
    list_filter = (
        "timestamp",
        ("event__application", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        "status",
        ("recipients", NumberFilter),
    )
    readonly_fields = ["correlation_id"]
    ordering = ("-timestamp",)

    def get_list_display(self, request: HttpRequest) -> list[str]:  # type: ignore[override]
        return super().get_list_display(request)  # type: ignore[return-value]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Occurrence]:
        return super().get_queryset(request).select_related("event__application")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Occurrence | None = None) -> bool:
        return False

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        visible=lambda btn: btn.original.status == btn.original.Status.NEW,
    )
    def process(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj = self.get_object(request, pk)
        obj.process()

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_occurrence",
    )
    def purge(self, request: HttpRequest) -> HttpResponse:  # noqa
        purge_occurrences.delay()
        self.message_user(request, _("Occurrence purge has been successfully triggered"), messages.INFO)

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_occurrence",
    )
    def payload(self, request: HttpRequest, pk: str) -> TemplateResponse:  # noqa
        ctx = self.get_common_context(request, pk)
        ctx["media"] = Media(css={"screen": ["bitcaster/css/pygments.css"]})
        return TemplateResponse(request, "admin/bitcaster/occurrence/payload.html", ctx)
