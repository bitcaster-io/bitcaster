import logging
from unittest import mock

from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from constance import config
from django.contrib import messages
from django.contrib.admin import display
from django.db.models import QuerySet
from django.forms.widgets import Media
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Occurrence
from bitcaster.tasks import purge_occurrences

from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor

logger = logging.getLogger(__name__)


class OccurrenceAdmin(BaseAdmin, BitcasterModelAdmin[Occurrence]):
    search_fields = ("name",)
    list_display = ("timestamp", "application", "event", "status", "paused", "attempts", "recipients")
    list_filter = (
        "timestamp",
        ("event__application", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        "status",
    )
    fieldsets = (
        (
            _("General"),
            {
                "classes": ["tab"],
                "fields": [
                    "timestamp",
                    "event",
                    "newsletter",
                ],
            },
        ),
        (
            _("Process"),
            {
                "classes": ["tab"],
                "fields": [
                    "attempts",
                    "status",
                ],
            },
        ),
        (
            _("Input"),
            {
                "classes": ["tab"],
                "fields": [
                    "correlation_id",
                    "context",
                    "options",
                ],
            },
        ),
        (
            _("Delivery"),
            {
                "classes": ["tab"],
                "fields": [
                    "recipients",
                    "data",
                ],
            },
        ),
    )
    readonly_fields = ["correlation_id"]
    ordering = ("-timestamp",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Occurrence]:
        return super().get_queryset(request).select_related("event__application")

    @display(boolean=True)
    def paused(self, obj: Occurrence):
        return obj.event.paused or obj.event.application.paused

    def get_list_display(self, request: HttpRequest) -> list[str]:  # type: ignore[override]
        return super().get_list_display(request)  # type: ignore[return-value]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Occurrence | None = None) -> bool:
        return False

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        visible=lambda btn: btn.original.status == btn.original.Status.NEW,
    )
    def inspect(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj: Occurrence = self.get_object(request, pk)

        def doit(request):
            try:
                ctx = self.get_common_context(request, obj)
                if obj.status == Occurrence.Status.NEW:
                    with mock.patch("bitcaster.models.notification.Notification.notify_to_channel"):
                        data = obj._process()
                        ctx["data"] = data
                    return TemplateResponse(request, "bitcaster/admin/occurrence/inspect.html", ctx)
            except Exception as e:
                logger.exception(e)
                self.message_user(request, _("Error processing occurrence"), messages.ERROR)

        return confirm_action(
            self,
            request,
            doit,
            message="Proceeding will process the occurrence",
            success_message="",
            description=_(""),
            extra_context={"content_title": "Process", "object": obj, "opts": obj._meta},
            error_message="",
        )

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        visible=lambda btn: btn.original.status == btn.original.Status.NEW,
    )
    def process(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj: Occurrence = self.get_object(request, pk)

        def doit(request):
            try:
                if obj.process():
                    self.message_user(request, _("Occurrence has been successfully processed"), messages.SUCCESS)
                    self.message_user(request, f"{obj.data}", messages.INFO)
                else:
                    self.message_user(
                        request,
                        _("Occurrence has been processed, but no recipients have been reached out"),
                        messages.WARNING,
                    )
            except Exception as e:
                logger.exception(e)
                self.message_user(request, _("Error processing occurrence"), messages.ERROR)

        return confirm_action(
            self,
            request,
            doit,
            message="Proceeding will process the occurrence",
            success_message="",
            description=_(""),
            extra_context={"content_title": "Process", "object": obj, "opts": obj._meta},
            error_message="",
        )

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_occurrence",
    )
    def purge(self, request: HttpRequest) -> HttpResponse:  # noqa
        def doit(request) -> "HttpResponse|None":
            purge_occurrences.delay()
            self.message_user(request, _("Occurrence purge has been successfully triggered"), messages.SUCCESS)

        return confirm_action(
            self,
            request,
            doit,
            message=f"Proceeding will delete all occurrences older than {config.OCCURRENCE_DEFAULT_RETENTION} days",
            success_message="",
            description=_("All data will be permanently removed. No rollback action available"),
            title=_("Purge occurrences"),
            extra_context={"action_title": "Purge occurrences"},
            error_message="",
        )

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_occurrence",
    )
    def payload(self, request: HttpRequest, pk: str) -> TemplateResponse:  # noqa
        obj = self.get_object(request, pk)
        ctx = self.get_common_context(request, pk, action_title="Payload", object=obj, opts=obj._meta)
        ctx["media"] = Media(css={"screen": ["bitcaster/css/pygments.css"]})
        return TemplateResponse(request, "bitcaster/admin/occurrence/payload.html", ctx)

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_occurrence",
    )
    def add_notification(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:  # noqa
        obj: Occurrence = self.get_object(request, pk)
        base_url = reverse("admin:bitcaster_notification_add")
        url = f"{base_url}?event={obj.event.pk}&name=Auto%20notification%20for%20{obj.event.name}"
        return HttpResponseRedirect(url)
