import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from bitcaster.models import Notification

from .base import BaseAdmin

if TYPE_CHECKING:
    from bitcaster.models import Channel, Message


logger = logging.getLogger(__name__)


class NotificationAdmin(BaseAdmin, admin.ModelAdmin[Notification]):
    search_fields = ("name",)
    list_display = ("name", "event")
    list_filter = (
        ("event__application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        (
            "event__application__project",
            LinkedAutoCompleteFilter.factory(parent="event__application__project__organization"),
        ),
        ("event__application", LinkedAutoCompleteFilter.factory(parent="event__application__project")),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        # ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
    autocomplete_fields = ("event", "distribution")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Notification]:
        return super().get_queryset(request).select_related("event", "distribution")

    @button()
    def messages(self, request: HttpRequest, pk: str) -> HttpResponse:
        ctx = self.get_common_context(request, pk, title=_("Message resolution order"))
        obj: Notification = ctx["original"]
        messages: "dict[Channel, QuerySet[Message]]" = {}
        for ch in obj.event.channels.all():
            messages[ch] = obj.get_messages(ch)
        ctx["message_templates"] = messages
        return TemplateResponse(request, "admin/notification/messages.html", ctx)
