import logging
from typing import TYPE_CHECKING, Any
from unittest import mock

from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from constance import config
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.decorators import display

from bitcaster.models import Assignment, Channel, MessageTemplate, Notification, Occurrence
from bitcaster.runner.tasks import purge_occurrences

from ..cache.manager import CacheManager
from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor

if TYPE_CHECKING:
    from ..models.occurrence import OccurrenceData

logger = logging.getLogger(__name__)


class OccurrenceAdmin(BaseAdmin, BitcasterModelAdmin[Occurrence]):
    search_fields = ("name",)
    list_display = ("pk", "timestamp", "application", "event", "status_badge", "paused", "attempts", "recipients")
    list_filter = (
        "timestamp",
        ("event__application", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        "status",
    )
    fieldsets = (
        (_("General"), {"classes": ["tab"], "fields": ["timestamp", "event", "newsletter"]}),
        (_("Process"), {"classes": ["tab"], "fields": ["attempts", "status"]}),
        (_("Input"), {"classes": ["tab"], "fields": ["correlation_id", "context", "options"]}),
        (_("Delivery"), {"classes": ["tab"], "fields": ["recipients", "data"]}),
    )
    readonly_fields = ["correlation_id"]
    ordering = ("-timestamp",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Occurrence]:
        return super().get_queryset(request).select_related("event__application")

    @display(boolean=True)
    def paused(self, obj: Occurrence):
        return obj.event.paused or obj.event.application.paused

    @display(
        ordering="status",
        label={
            Occurrence.Status.PROCESSED: "success",  # green
            Occurrence.Status.FAILED: "danger",  # green
            Occurrence.Status.NEW: "info",  # green
        },
    )
    def status_badge(self, obj):
        return obj.status

    def get_list_display(self, request: HttpRequest) -> list[str]:  # type: ignore[override]
        return super().get_list_display(request)  # type: ignore[return-value]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Occurrence | None = None) -> bool:
        return False

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def inspect(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj: Occurrence = self.get_queryset(request).select_related("event__application").get(id=pk)

        def inspect(req):
            dm = CacheManager(req)
            version = dm.get_version(f"inspect:{obj.pk}")
            base_key = f"inspect:{obj.pk}:{version}"
            with dm.activate_namespace(base_key):
                try:
                    notes = []
                    if not (extra_context := dm.retrieve("extra_context")):
                        active_notifications = [p.pk for p in obj._get_valid_notifications()]
                        active_channels = obj._get_valid_channels()
                        message_for_channel = {
                            msg.channel.pk: msg for msg in MessageTemplate.objects.filter(notification__event=obj.event)
                        }
                        for nt in obj.event.notifications.filter(id__in=active_notifications):
                            for ch in active_channels:
                                message_for_channel.setdefault(ch.pk, (ch, nt, nt.get_message(ch)))
                        all_messages = obj.event.messages.all()
                        extra_context = {
                            "notifications": obj.event.notifications.select_related("distribution").all(),
                            "active_notifications": active_notifications,
                            "active_channels": list(active_channels.values_list("pk", flat=True)),
                            "messages": message_for_channel,
                            "all_messages": all_messages,
                        }
                        dm.store("extra_context", extra_context)

                    if not extra_context["active_notifications"]:
                        if not obj.event.notifications.filter(active=True).exists():
                            notes.append(["warning", _("This event does not have any notification")])
                        else:
                            notes.append(["warning", _("No active notifications for this event")])
                    if not extra_context["active_channels"]:
                        notes.append(["warning", _("No active channels enabled for this event")])
                    if not extra_context["messages"]:
                        notes.append(["warning", _("No messages configured for selected channels")])

                    ctx = self.get_common_context(
                        req, pk, action_title="Inspect", statuses=Occurrence.Status, notes=notes, **extra_context
                    )
                    # Processing info
                    data: "OccurrenceData"
                    assignments = dm.retrieve("assignments")
                    recipients = dm.retrieve("recipients")

                    if not assignments or not recipients:
                        if obj.status == Occurrence.Status.NEW:

                            def collect_info(
                                n: "Notification", channel: "Channel", assignment: "Assignment", context: dict[str, Any]
                            ):
                                return assignment.address.value, n.get_message(channel).pk

                            with mock.patch(
                                "bitcaster.models.notification.Notification.notify_to_channel", collect_info
                            ):
                                __, data = obj._process()
                        else:
                            data = obj.data
                        recipients = data.get("recipients", [])
                        assignment_pks = [e[2] for e in recipients]
                        assignments = (
                            Assignment.objects.select_related("address__user", "channel")
                            .filter(pk__in=assignment_pks)
                            .in_bulk()
                        )
                        dm.store("assignments", assignments)
                        dm.store("recipients", recipients)

                    ctx["assignments"] = assignments
                    ctx["recipients"] = recipients
                    return TemplateResponse(req, "bitcaster/admin/occurrence/inspect.html", ctx)
                except Exception as e:
                    logger.exception(e)
                    self.message_user(req, _("Error inspecting occurrence"), messages.ERROR)

        if obj.status == Occurrence.Status.NEW:
            return confirm_action(
                self,
                request,
                inspect,
                message="Proceeding will take some time",
                success_message="",
                description="",
                extra_context={"content_title": "Inspect", "object": obj, "opts": obj._meta},
                error_message="",
            )

        return inspect(request)

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
            description="",
            extra_context={"content_title": "Process", "object": obj, "opts": obj._meta},
            error_message="",
        )

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_occurrence",
    )
    def purge(self, request: HttpRequest) -> HttpResponse:  # noqa
        def doit(request) -> "HttpResponse|None":
            purge_occurrences.send()
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
    def add_notification(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:  # noqa
        obj: Occurrence = self.get_object(request, pk)
        base_url = reverse("admin:bitcaster_notification_add")
        url = f"{base_url}?event={obj.event.pk}&name=Auto%20notification%20for%20{obj.event.name}"
        return HttpResponseRedirect(url)
