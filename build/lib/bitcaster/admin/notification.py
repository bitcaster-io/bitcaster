import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from ..forms.message import NotificationTemplateCreateForm
from ..forms.notification import NotificationForm
from .base import BaseAdmin, ButtonColor

if TYPE_CHECKING:
    from bitcaster.models import Notification

logger = logging.getLogger(__name__)


class NotificationAdmin(BaseAdmin, admin.ModelAdmin["Notification"]):
    search_fields = ("name",)
    list_display = ("name", "event", "application")
    list_filter = (
        # ("event__application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        # (
        #     "event__application__project",
        #     LinkedAutoCompleteFilter.factory(parent="event__application__project__organization"),
        # ),
        ("event__application", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        ("distribution__recipients__address__user", LinkedAutoCompleteFilter.factory(parent=None)),
    )
    autocomplete_fields = ("event", "distribution")
    form = NotificationForm

    def get_exclude(self, request: HttpRequest, obj: "Notification | None" = None) -> tuple[str, ...]:
        return ("payload_filter", "extra_context")

    def get_queryset(self, request: HttpRequest) -> QuerySet["Notification"]:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "event",
                "event__application",
                "event__application__project",
                "event__application__project__organization",
                "distribution",
            )
        )

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def messages(self, request: HttpRequest, pk: str) -> HttpResponse:
        status_code = 200
        ctx = self.get_common_context(request, pk, title=_("Messages"))
        notification: "Notification" = ctx["original"]
        if request.method == "POST":
            form = NotificationTemplateCreateForm(request.POST, notification=notification)
            if form.is_valid():
                msg = notification.create_message(name=form.cleaned_data["name"], channel=form.cleaned_data["channel"])
                ctx["message_created"] = msg
            else:
                status_code = 400
        else:
            form = NotificationTemplateCreateForm(notification=notification)
        ctx["message_templates"] = notification.messages.filter()
        ctx["form"] = form
        return TemplateResponse(request, "admin/notification/messages.html", ctx, status=status_code)
