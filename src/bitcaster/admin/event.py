from typing import TYPE_CHECKING, Any, Sequence

import logging
from datetime import timedelta

from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from constance import config
from unfold import widgets as uwidgets
from unfold.decorators import display

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import bitcaster
from bitcaster.forms.event import API_PAYLOAD_SKELETON, EventChangeForm, EventDebugForm
from bitcaster.forms.unfold import UnfoldAdminForm
from bitcaster.models import Assignment, Event, EventSimulation, Occurrence
from bitcaster.runner.tasks import run_event_simulation
from bitcaster.state import state

from .base import BaseAdmin, ButtonColor
from .message import MessageTemplate
from .mixins import LockMixinAdmin, TwoStepCreateMixin
from .simulation import simulation_page, simulation_results_context
from ..utils.widgets import SmartMedia

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.admin.options import _FieldsetSpec
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class MessageInline(admin.TabularInline[MessageTemplate, Event]):
    model = MessageTemplate
    extra = 0
    fields = [
        "name",
    ]
    show_change_link = True


class EventTestForm(forms.Form):
    assignment = forms.ModelChoiceField(queryset=Assignment.objects.none(), widget=uwidgets.UnfoldAdminSelectWidget)


class EventAdmin(TwoStepCreateMixin[Event], LockMixinAdmin[Event], BaseAdmin[Event]):
    search_fields = ("name",)
    list_display = ("name", "application", "simulation_badge", "active", "locked")
    list_filter = (
        ("application__project", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
        ("channels", AutoCompleteFilter),
        ("notifications__distribution", LinkedAutoCompleteFilter.factory(parent=None)),
        ("notifications__distribution__recipients__address__user", LinkedAutoCompleteFilter.factory(parent=None)),
        "active",
        "locked",
    )
    autocomplete_fields = ("application",)
    filter_horizontal = ("channels",)
    form = EventChangeForm
    save_as_continue = False
    save_as = False
    _fieldsets: "_FieldsetSpec" = [
        (
            None,
            {
                "fields": (
                    ("application",),
                    ("name", "slug"),
                    ("description",),
                    ("active", "newsletter", "paused"),
                    ("occurrence_retention",),
                )
            },
        ),
        (
            "",
            {
                "fields": ["channels"],
            },
        ),
    ]
    change_form_template = "bitcaster/admin/event/change_form.html"

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/js/jquery.init.js", "bitcaster/js/copy.js"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")

    def has_delete_permission(self, request: HttpRequest, obj: Event | None = None) -> bool:
        if obj and obj.application.project.organization.name == bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request, obj)

    def get_fieldsets(self, request: HttpRequest, obj: Event | None = None) -> "_FieldsetSpec":
        if obj:
            return self._fieldsets
        return [(None, {"fields": list(self.get_fields(request, obj))})]

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Event]) -> None:
        queryset.exclude(application__project__organization__name=bitcaster.ORGANIZATION).delete()

    def get_deleted_objects(
        self, objs: QuerySet[Event] | Sequence[Event], request: HttpRequest
    ) -> tuple[list[Any] | Any, dict[str, Any] | Any, set[Any] | Any, list[Any] | Any]:
        if isinstance(objs, QuerySet):
            objs = objs.exclude(application__project__organization__name=bitcaster.ORGANIZATION)
            to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        elif objs[0].application.project.organization.name == bitcaster.ORGANIZATION:
            to_delete, model_count, perms_needed, protected = [], {}, set(), objs  # type: ignore[assignment]
        else:
            to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        return to_delete, model_count, perms_needed, protected

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", str(request.user.id))
        initial.setdefault("organization", state.get_cookie("organization"))
        initial.setdefault("from_email", str(request.user.email))
        return initial

    def get_readonly_fields(self, request: HttpRequest, obj: Event | None = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["application", "slug"]
        return []

    def get_fields(self, request: HttpRequest, obj: Event | None = None) -> list[Any]:
        form = self._get_form_for_get_fields(request, obj)
        return [*self.get_readonly_fields(request, obj), *form.base_fields]

    def get_exclude(self, request: HttpRequest, obj: Event | None = None) -> "_ListOrTuple[str]":
        if obj is None:
            return ["channels", "locked"]
        return ["locked"]

    @button(html_attrs={"class": ButtonColor.ACTION.value}, permission="bitcaster.trigger_event")  # type: ignore[arg-type]
    def trigger_event(self, request: HttpRequest, pk: str) -> HttpResponse:
        def get_form(*args: Any, **kwargs: Any) -> EventTestForm:
            frm = EventTestForm(*args, **kwargs)
            frm.fields["assignment"].queryset = Assignment.objects.filter(
                distributionlist__recipients__address__user=request.user
            ).distinct()
            return frm

        context = self.get_common_context(request, pk, action_title=_("Trigger Event"))
        evt: Event = self.get_object_or_404(request, pk)
        if request.method == "POST":
            config_form = get_form(request.POST)
            if config_form.is_valid():
                try:
                    o: Occurrence = evt.trigger(
                        context={},
                        options={
                            "limit_to": [config_form.cleaned_data["assignment"].address.value],
                            "channels": [config_form.cleaned_data["assignment"].channel.pk],
                        },
                    )
                    o.process()
                    self.message_user(request, f"Sent {o.status} - {o.data}", messages.SUCCESS)
                    return HttpResponseRedirect(".")
                except Exception as e:
                    logger.exception(e)
                    self.message_user(request, str(e), level=messages.ERROR)
        else:
            config_form = get_form(
                initial={
                    "subject": "[TEST] Subject",
                    "message": "aaa",
                }
            )
        context["form"] = config_form
        return TemplateResponse(request, "bitcaster/admin/event/test_event.html", context)

    @display(label={"simulation running": "info"})  # type: ignore[untyped-decorator]
    def simulation_badge(self, obj: Event) -> str:
        if obj.simulations.filter(status=Occurrence.Status.NEW).exists():
            return "simulation running"
        return ""

    @button(  # type: ignore[arg-type]
        label=_("Simulate"),
        html_attrs={"class": ButtonColor.ACTION.value},
        permission="bitcaster.debug_event",
    )
    def debug_event(self, request: HttpRequest, pk: str) -> HttpResponse:
        def get_form(*args: Any, **kwargs: Any) -> EventDebugForm:
            return EventDebugForm(*args, event=evt, **kwargs)

        evt: Event = self.get_object_or_404(request, pk)
        context = self.get_common_context(request, pk, action_title=_("Simulate"))
        context["original"] = evt
        session_key = f"event_debug_context_{evt.pk}"
        simulation: EventSimulation | None = None

        if simulation_pk := request.GET.get("simulation"):
            try:
                simulation_pk = int(simulation_pk)
                simulation = EventSimulation.objects.get(pk=simulation_pk)
                if simulation.event_id != evt.pk:
                    raise Http404
            except (EventSimulation.DoesNotExist, ValueError):
                simulation = None
                context["stale_simulation"] = True

        if simulation:
            if simulation.status == Occurrence.Status.NEW and simulation.timestamp < timezone.now() - timedelta(
                minutes=config.EVENT_SIMULATION_TIMEOUT
            ):
                EventSimulation.objects.filter(pk=simulation.pk, status=Occurrence.Status.NEW).update(
                    status=Occurrence.Status.FAILED, data={"errors": ["simulation timed out"]}
                )
                simulation.refresh_from_db()
            context["simulation"] = simulation
            context["mode"] = simulation.mode
            if simulation.data:
                context.update(simulation_results_context(simulation, simulation_page(simulation, request)))

        if request.method == "POST":
            config_form = get_form(request.POST)
            if config_form.is_valid():
                ctx: dict[str, Any] = config_form.cleaned_data.get("context") or {}
                opts = config_form.get_options()
                mode = config_form.cleaned_data["mode"]
                request.session[session_key] = ctx
                EventSimulation.objects.filter(event=evt).delete()
                simulation = EventSimulation.objects.create(
                    event=evt, created_by=request.user, context=ctx, options=opts, mode=mode
                )
                if mode != "fast":
                    run_event_simulation.send(simulation.pk)
                    return HttpResponseRedirect(f"{request.path}?simulation={simulation.pk}")
                try:
                    limit = config.DEBUG_PREVIEW_RENDER_LIMIT if mode == "partial" else None
                    occurrence = Occurrence(event=evt, context=ctx, options=opts)
                    _success, data = occurrence.preview(mode, limit)
                    simulation.save_deliveries(data)
                except Exception as e:
                    logger.exception(e)
                    EventSimulation.objects.filter(pk=simulation.pk, status=Occurrence.Status.NEW).update(
                        data={"errors": [f"{e.__class__.__name__}: {str(e)}"]}, status=Occurrence.Status.FAILED
                    )
                return HttpResponseRedirect(f"{request.path}?simulation={simulation.pk}")
        else:
            initial: dict[str, Any] = {}
            if simulation:
                initial = {
                    "context": simulation.context,
                    "mode": simulation.mode,
                    "limit_to": ", ".join(str(e) for e in simulation.options.get("limit_to", [])),
                    "channels": [int(pk) for pk in simulation.options.get("channels", []) if str(pk).isdigit()],
                    "api_payload": {"payload_context": simulation.context, "options": simulation.options},
                }
            else:
                initial["context"] = request.session.get(session_key, {})
                initial["channels"] = [
                    channel.pk for channel in evt.channels.filter(active=True, locked=False, paused=False)
                ]
                initial["api_payload"] = API_PAYLOAD_SKELETON
            config_form = get_form(initial=initial)
        context["form"] = config_form
        fs = (
            (
                _("General"),
                {"classes": ["tab"], "fields": ["mode", "context", "limit_to", "channels"]},
            ),
            (_("Emulate API call"), {"classes": ["tab"], "fields": ["api_payload"]}),
        )
        context["admin_form"] = UnfoldAdminForm(config_form, fs, {}, model_admin=self)
        return TemplateResponse(request, "bitcaster/admin/event/debug_event.html", context)

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def notifications(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_notification_changelist")
        event: Event = button.context["original"]
        if event:
            button.href = f"{url}?event__exact={event.pk}&event__application__exact={event.application.pk}"
        else:
            button.visible = False

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def occurrences(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_occurrence_changelist")
        event: Event = button.context["original"]
        if event:
            button.href = f"{url}?event__exact={event.pk}&event__application__exact={event.application.pk}"
        else:
            button.visible = False

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def messages(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_messagetemplate_changelist")
        event: Event = button.context["original"]
        if event:
            button.href = f"{url}?event__exact={event.pk}"
        else:
            button.visible = False

    @button(
        label=_("Extra"),
        html_attrs={"class": ButtonColor.ACTION.value},
    )
    def trigger_instructions(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import ApiKey

        media = SmartMedia(
            js=["admin/js/vendor/jquery/jquery{min}.js", "admin/js/jquery.init.js", "bitcaster/js/copy{min}.js"]
        )
        context = self.get_common_context(request, pk, action_title=_("Trigger Instructions"), media=media)
        event: Event = context["original"]

        context["trigger_url"] = event.get_trigger_url()

        can_read_apikeys = request.user.has_perm("bitcaster.view_apikey")
        context["can_read_apikeys"] = can_read_apikeys
        if can_read_apikeys and event.application:
            context["api_keys"] = ApiKey.objects.filter(application=event.application).values("id", "name", "key")
        else:
            context["api_keys"] = []

        return TemplateResponse(request, "bitcaster/admin/event/trigger_instructions.html", context)
