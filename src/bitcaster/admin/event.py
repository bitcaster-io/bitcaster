import logging
from typing import TYPE_CHECKING, Any, Optional, Sequence

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from bitcaster.models import Event

from ..forms.event import EventChangeForm
from ..state import state
from .base import BaseAdmin
from .message import Message
from .mixins import LockMixinAdmin, TwoStepCreateMixin

if TYPE_CHECKING:
    from django.http import HttpResponse
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class MessageInline(admin.TabularInline[Message, Event]):
    model = Message
    extra = 0
    fields = [
        "name",
    ]
    show_change_link = True


class EventTestForm(forms.Form):
    recipient = forms.CharField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class EventAdmin(BaseAdmin, TwoStepCreateMixin[Event], LockMixinAdmin[Event], admin.ModelAdmin[Event]):
    search_fields = ("name",)
    list_display = ("name", "application", "active", "locked")
    list_filter = (
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
        ("channels", AutoCompleteFilter),
        "active",
        "locked",
    )
    autocomplete_fields = ("application",)
    filter_horizontal = ("channels",)
    form = EventChangeForm
    save_as_continue = False
    save_as = False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", request.user.id)
        initial.setdefault("organization", state.get_cookie("organization"))
        initial.setdefault("from_email", request.user.email)
        return initial

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[Event]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["application", "slug", "name"]
        return []

    def get_fields(self, request: HttpRequest, obj: Optional[Event] = None) -> Sequence[str | Sequence[str]]:
        form = self._get_form_for_get_fields(request, obj)
        return [*self.get_readonly_fields(request, obj), *form.base_fields]

    def get_exclude(self, request: "HttpRequest", obj: "Optional[Event]" = None) -> "_ListOrTuple[str]":
        if obj is None:
            return ["channels", "locked"]
        else:
            return ["locked"]

    @button()
    def trigger_event(self, request: HttpRequest, pk: str) -> "HttpResponse":
        obj: Optional[Event] = self.get_object(request, pk)
        url = obj.get_trigger_url(request)
        self.message_user(request, url, messages.SUCCESS)

    @button()
    def notifications(self, request: HttpRequest, pk: str) -> "HttpResponse":
        ctx = self.get_common_context(request, pk, title=_("Notifications"))
        # ctx[""]
        return TemplateResponse(request, "admin/event/notifications.html", ctx)
