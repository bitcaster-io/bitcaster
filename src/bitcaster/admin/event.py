import logging
from typing import TYPE_CHECKING, Any, Optional, Sequence

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Event

from ..forms.event import EventChangeForm
from ..state import state
from .base import BaseAdmin
from .message import Message
from .mixins import LockMixin, TwoStepCreateMixin

if TYPE_CHECKING:
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


class EventAdmin(BaseAdmin, TwoStepCreateMixin[Event], LockMixin[Event], admin.ModelAdmin[Event]):
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
    # inlines = [MessageInline]
    form = EventChangeForm
    # add_form = EventAddForm
    save_as_continue = False
    save_as = False
    # change_form_template = None

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {"application": state.get_cookie("application")}

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[Event]" = None) -> "_ListOrTuple[str]":
        #     if request.user.has_perm("bitcaster.lock_system"):
        #         return ["application", "slug", "name"]
        return ["locked"]

    def get_fields(self, request: HttpRequest, obj: Optional[Event] = None) -> Sequence[str | Sequence[str]]:
        form = self._get_form_for_get_fields(request, obj)
        return [*self.get_readonly_fields(request, obj), *form.base_fields]

    def get_exclude(self, request: "HttpRequest", obj: "Optional[Event]" = None) -> "_ListOrTuple[str]":
        if obj is None:
            return ["channels", "locked"]
        else:
            return ["locked"]

    # @button(
    #     visible=lambda s: s.context["original"].channels.exists(),
    #     html_attrs={"style": f"background-color:{ButtonColor.ACTION}"},
    # )
    # def test_event(self, request: HttpRequest, pk: str) -> "Union[HttpResponseRedirect, HttpResponse]":
    #     obj = self.get_object(request, pk)
    #     context = self.get_common_context(request, pk, title=_(f"Test event {obj}"))
    #     if request.method == "POST":
    #         form = EventTestForm(request.POST)
    #         if form.is_valid():
    #             url = reverse("admin:bitcaster_event_change", args=[obj.id])
    #             messages.success(request, _(f"Test for event {obj} successful"))
    #             return HttpResponseRedirect(url)
    #     else:
    #         form = EventTestForm()
    #     context["test_form"] = form
    #     return TemplateResponse(request, "admin/event/test_event.html", context)
