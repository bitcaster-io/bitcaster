from typing import cast

import logging

from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import button, link
from constance import config
from unfold.decorators import display

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from bitcaster.models import EventSimulation, Occurrence
from bitcaster.runner.tasks import purge_event_simulations

from .base import BaseAdmin, ButtonColor
from .simulation import simulation_page, simulation_results_context

logger = logging.getLogger(__name__)


class EventSimulationAdmin(BaseAdmin[EventSimulation]):
    list_display = ("pk", "timestamp", "event", "status_badge", "deliveries_link")
    ordering = ("-timestamp",)
    change_form_template = "bitcaster/admin/eventsimulation/change_form.html"
    fieldsets = (
        (_("General"), {"classes": ["tab"], "fields": ["timestamp", "event", "created_by"]}),
        (
            _("Trigger"),
            {"classes": ["tab"], "fields": ["payload", "mode", "status"]},
        ),
        (_("Result"), {"classes": ["tab"], "fields": ["data"]}),
    )
    readonly_fields = ["payload"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[EventSimulation]:
        return super().get_queryset(request).select_related("event").annotate(deliveries_count=Count("deliveries"))

    @display(  # type: ignore[untyped-decorator]
        description=_("How the simulation was triggered"),
    )
    def payload(self, obj: EventSimulation) -> str:
        import json

        payload = {"payload_context": obj.context, "options": obj.options}
        return format_html("<pre>{}</pre>", json.dumps(payload, indent=2, default=str))

    @display(  # type: ignore[untyped-decorator]
        description=_("Invoke the same call with curl"),
    )
    def curl_command(self, obj: EventSimulation) -> str:
        import json

        url = reverse(
            "api:event-trigger",
            args=[
                obj.event.application.project.organization.slug,
                obj.event.application.project.slug,
                obj.event.application.slug,
                obj.event.slug,
            ],
        )
        payload = json.dumps({"payload_context": obj.context, "options": obj.options})
        command = (
            "curl -X POST \\\n"
            f'  -H "Authorization: Key <API_KEY>" \\\n'
            f'  -H "Content-Type: application/json" \\\n'
            f"  -d '{payload}' \\\n"
            f"  https://<HOST>{url}"
        )
        return format_html("<pre>{}</pre>", command)

    def get_list_display(self, request: HttpRequest) -> list[str]:  # type: ignore[override]
        return cast("list[str]", super().get_list_display(request))

    def changeform_view(  # type: ignore[override]
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, object] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        if object_id and (obj := self.get_object(request, object_id)):
            extra_context["curl_command"] = self.curl_command(obj)
        return super().changeform_view(request, object_id, form_url, extra_context)

    @display(  # type: ignore[untyped-decorator]
        ordering="status",
        label={
            Occurrence.Status.PROCESSED: "success",
            Occurrence.Status.FAILED: "danger",
            Occurrence.Status.NEW: "info",
        },
    )
    def status_badge(self, obj: EventSimulation) -> str:
        return str(obj.status)

    @link(change_form=True, change_list=False, label=_("Delivery simulations"))  # type: ignore[arg-type]
    def view_deliveries(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_deliverysimulation_changelist")
        simulation: EventSimulation = button.context["original"]
        if simulation:
            button.href = f"{url}?simulation__exact={simulation.pk}"
        else:
            button.visible = False

    def deliveries_link(self, obj: EventSimulation) -> str:
        url = reverse("admin:bitcaster_eventsimulation_deliveries", args=[obj.pk])
        return format_html(
            '<a href="{url}">{label} ({count})</a>',
            url=url,
            label=_("View deliveries"),
            count=obj.deliveries_count,
        )

    deliveries_link.short_description = _("Deliveries")  # type: ignore[attr-defined]

    def get_urls(self) -> list:
        urls = [
            path(
                "<path:object_id>/deliveries/",
                self.admin_site.admin_view(self.deliveries),
                name="bitcaster_eventsimulation_deliveries",
            ),
        ]
        return urls + super().get_urls()

    def deliveries(self, request: HttpRequest, object_id: str) -> HttpResponse:
        simulation = self.get_object_or_404(request, object_id)
        if not self.has_view_or_change_permission(request, simulation):
            raise PermissionDenied
        page = simulation_page(simulation, request)
        context = {
            **self.admin_site.each_context(request),
            "title": str(_("Delivery simulations")),
            "original": simulation,
            **simulation_results_context(simulation, page),
        }
        return TemplateResponse(request, "bitcaster/admin/eventsimulation/deliveries.html", context)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: EventSimulation | None = None) -> bool:
        return False

    @button(  # type: ignore[arg-type]
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.delete_eventsimulation",
    )
    def purge(self, request: HttpRequest) -> HttpResponse:  # noqa
        def doit(req: HttpRequest) -> None:
            purge_event_simulations.send()
            self.message_user(req, str(_("Event simulations purge has been successfully triggered")), messages.SUCCESS)

        return confirm_action(
            self,
            request,
            doit,
            message=f"Proceeding will delete all event simulations older than {config.EVENT_SIMULATION_RETENTION} days",
            success_message="",
            description=str(_("All data will be permanently removed. No rollback action available")),
            title=str(_("Purge event simulations")),
            extra_context={"action_title": "Purge event simulations"},
            error_message="",
        )
