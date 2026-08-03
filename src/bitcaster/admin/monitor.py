from typing import TYPE_CHECKING

import logging

from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from reversion.admin import VersionAdmin

from django import forms
from django.contrib import messages
from django.contrib.admin.helpers import AdminForm
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from bitcaster.forms.monitor import MonitorForm
from bitcaster.models import Channel, Monitor

from .base import BaseAdmin, ButtonColor
from .mixins import TwoStepCreateMixin

if TYPE_CHECKING:  # pragma: no cover
    from bitcaster.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class MonitorTestForm(forms.Form):
    pass


class MonitorScheduleForm(forms.Form):
    pass


class MonitorAdmin(BaseAdmin[Monitor], TwoStepCreateMixin[Monitor], VersionAdmin[Monitor]):
    search_fields = ("name",)
    list_display = (
        "name",
        "event",
        "agent_",
        "active",
    )
    list_filter = (
        ("event__application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        (
            "event__application__project",
            LinkedAutoCompleteFilter.factory(parent="event__application__project__organization"),
        ),
        ("event__application", LinkedAutoCompleteFilter.factory(parent="event__application__project")),
        "active",
    )
    autocomplete_fields = ("event",)
    change_list_template = "admin_extra_buttons/change_list.html"
    form = MonitorForm

    def agent_(self, obj: Monitor) -> str:
        return str(obj.agent)

    def get_queryset(self, request: "HttpRequest") -> QuerySet[Monitor]:
        return super().get_queryset(request).select_related("event", "event__application__project")

    @link(change_form=True, change_list=False)
    def events(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_event_changelist")
        ch: Channel = button.context["original"]
        if ch:
            button.href = f"{url}?channels__exact={ch.pk}"
        else:
            button.visible = False

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def configure(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        monitor: Monitor = self.get_object_or_404(request, pk)
        context = self.get_common_context(request, pk, action_title=_("Configure Monitor"))
        form_class = monitor.agent.config_class
        if request.method == "POST":
            config_form = form_class(request.POST)
            if config_form.is_valid():
                monitor.config = config_form.cleaned_data
                monitor.data = {}
                monitor.result = {}
                monitor.save()
                self.message_user(request, f"Configured Monitor {monitor.name}")
                next_url = request.GET.get("next")
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(monitor.get_admin_change())
        else:
            config_form = form_class(
                initial={k: v for k, v in monitor.config.items() if k in form_class.declared_fields}
            )
        fs = [(None, {"fields": list(form_class.declared_fields.keys())})]
        context["admin_form"] = AdminForm(config_form, fs, {})
        return TemplateResponse(request, "bitcaster/admin/monitor/configure.html", context)

    @button(html_attrs={"class": ButtonColor.ACTION.value})  # type: ignore[arg-type]
    def test(self, request: "AuthHttpRequest", pk: str) -> HttpResponse:
        monitor: Monitor = self.get_object_or_404(request, pk)
        context = self.get_common_context(request, pk, title=_("Test Monitor"))
        if request.method == "POST":
            try:
                monitor.agent.check(notify=False)
                if monitor.has_changes():
                    self.message_user(request, "Success. Changes detected", messages.WARNING)
                else:
                    self.message_user(request, "Success. No changes detected", messages.SUCCESS)
            except Exception as e:
                logger.exception(e)
                self.message_user(request, str(e), level=messages.ERROR)
        context["monitor"] = monitor
        context["form"] = MonitorTestForm()
        return TemplateResponse(request, "bitcaster/admin/monitor/test.html", context)
