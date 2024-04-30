import logging
from typing import TYPE_CHECKING, Optional, Union

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Event

from ..forms.event import EventChangeForm
from ..state import state
from .base import BUTTON_COLOR_ACTION, BaseAdmin
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


#
# class EventSubscribeForm(forms.Form):
#     channel_id = forms.IntegerField(widget=HiddenInput)
#     channel_name = forms.CharField()
#     address = forms.ChoiceField(label=_("Address"), choices=(("", "--"),), required=False)
#
#     def __init__(self, user: User, event: Event, **kwargs: Any):
#         address_choices = [[id, value] for id, value in Address.objects.filter(user=user).values_list("id", "value")]
#         initial = kwargs.get("initial")
#         if initial:
#             channel_id = initial["channel_id"]
#
#             subscription = Subscription.objects.filter(event=event, validation__channel_id=channel_id).first()
#             if subscription:
#                 initial["address"] = subscription.validation.address_id
#         super().__init__(**kwargs)
#         self.fields["address"].choices = list(self.fields["address"].choices) + list(address_choices)
#
#
# EventSubscribeFormSet = forms.formset_factory(EventSubscribeForm, extra=0)


class EventTestForm(forms.Form):
    recipient = forms.CharField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class EventAdmin(BaseAdmin, TwoStepCreateMixin, LockMixin, admin.ModelAdmin[Event]):
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
    inlines = [MessageInline]
    form = EventChangeForm
    # add_form = EventAddForm
    save_as_continue = False
    save_as = False
    # change_form_template = None

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")

    def get_changeform_initial_data(self, request):
        return {"application": state.get_cookie("application")}

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[Event]" = None) -> "_ListOrTuple[str]":
        if request.user.has_perm("bitcaster.lock_system"):
            return ["application", "slug", "name"]
        return ["locked"]

    def get_fields(self, request, obj=...):
        if self.fields:
            return self.fields
        form = self._get_form_for_get_fields(request, obj)
        return [*self.get_readonly_fields(request, obj), *form.base_fields]

    def get_exclude(self, request: "HttpRequest", obj: "Optional[Event]" = None):
        if obj is None:
            return ["channels", "locked"]
        else:
            return ["locked"]

    def get_inlines(self, request, obj=...):
        return super().get_inlines(request, obj)

    #
    # @button(html_attrs={"style": f"background-color:{BUTTON_COLOR_LINK}"})
    # def subscriptions(self, request: "HttpRequest", pk: str) -> "Union[HttpResponseRedirect]":
    #     obj = self.get_object(request, pk)
    #     base_url = reverse("admin:bitcaster_subscription_changelist")
    #     url = (
    #         f"{base_url}?event__exact={pk}"
    #         f"&event__application__project__organization__exact={obj.application.project.organization.id}"
    #         f"&event__application__project__exact={obj.application.project.id}"
    #         f"&event__application__exact={obj.application.id}"
    #     )
    #     return HttpResponseRedirect(url)
    #
    # @button(
    #     enabled=lambda s: s.context["original"].channels.exists(),
    #     html_attrs={"style": f"background-color:{BUTTON_COLOR_ACTION}"},
    # )
    # def subscribe(self, request: HttpRequest, pk: str) -> Union[HttpResponseRedirect, HttpResponse]:
    #     obj: Event = self.get_object(request, pk)
    #     context = self.get_common_context(request, pk, title=_(f"Subscribe to event {obj}"))
    #
    #     if request.method == "POST":
    #         context["formset"] = formset = EventSubscribeFormSet(
    #             data=request.POST,
    #             form_kwargs={"user": request.user, "event": obj},
    #         )
    #         if formset.is_valid():
    #             url = reverse("admin:bitcaster_event_change", args=[obj.id])
    #             for form in formset:
    #                 if address_id := form.cleaned_data["address"]:
    #                     obj.subscribe(int(address_id), form.cleaned_data["channel_id"])
    #                 else:
    #                     obj.unsubscribe(request.user, [form.cleaned_data["channel_id"]])
    #             messages.success(request, _(f"Subscribed to event {obj}."))
    #             return HttpResponseRedirect(url)
    #     else:
    #         context["formset"] = EventSubscribeFormSet(
    #             initial=[
    #                 {
    #                     "channel_id": channel.id,
    #                     "channel_name": channel.name,
    #                 }
    #                 for channel in obj.channels.all()
    #             ],
    #             form_kwargs={"user": request.user, "event": obj},
    #         )
    #     return TemplateResponse(request, "admin/event/subscribe_event.html", context)

    @button(
        visible=lambda s: s.context["original"].channels.exists(),
        html_attrs={"style": f"background-color:{BUTTON_COLOR_ACTION}"},
    )
    def test_event(self, request: HttpRequest, pk: str) -> "Union[HttpResponseRedirect, HttpResponse]":
        obj = self.get_object(request, pk)
        context = self.get_common_context(request, pk, title=_(f"Test event {obj}"))
        if request.method == "POST":
            context["test_form"] = EventTestForm(request.POST)
            url = reverse("admin:bitcaster_event_change", args=[obj.id])
            messages.success(request, _(f"Test for event {obj} successful"))
            return HttpResponseRedirect(url)
        else:
            context["test_form"] = EventTestForm()
        return TemplateResponse(request, "admin/event/test_event.html", context)
