import logging
from typing import Union

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Address, Event, Subscription

from .base import BaseAdmin
from .message import Message
from .mixins import LockMixin

logger = logging.getLogger(__name__)


class MessageInline(admin.TabularInline[Message, Event]):
    model = Message
    extra = 0
    fields = [
        "name",
    ]
    show_change_link = True


class EventSubscribeForm(forms.Form):
    channel_id = forms.IntegerField(widget=HiddenInput)
    channel_name = forms.CharField()
    address = forms.ChoiceField(label=_("Address"), choices=(("", "--"),), required=False)

    def __init__(self, channel_choices, **kwargs):
        # registered_addresses = kwargs.pop("registered_addresses", [])
        super().__init__(**kwargs)
        self.fields["address"].choices = list(self.fields["address"].choices) + list(channel_choices)


EventSubscribeFormSet = forms.formset_factory(EventSubscribeForm, extra=0)


class EventTestForm(forms.Form):
    recipient = forms.CharField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class EventAdmin(BaseAdmin, LockMixin, admin.ModelAdmin[Event]):
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")

    @button(visible=lambda s: s.context["original"].channels.exists(), html_attrs={"style": "background-color:green"})
    def subscribe(self, request: HttpRequest, pk: str) -> Union[HttpResponseRedirect, HttpResponse]:
        obj: Event = self.get_object(request, pk)
        context = self.get_common_context(request, pk, title=_(f"Subscribe to event {obj}"))
        channel_choices = request.user.addresses.values_list("id", "name")
        if request.method == "POST":
            context["formset"] = formset = EventSubscribeFormSet(
                data=request.POST, form_kwargs={"channel_choices": channel_choices}
            )
            if formset.is_valid():
                num_created = 0
                sub_created = 0
                url = reverse("admin:bitcaster_event_change", args=[obj.id])
                for form in formset:
                    if address_id := form.cleaned_data["address"]:
                        address = Address.objects.get(id=address_id)
                        subscription, created = Subscription.objects.get_or_create(address=address, event=obj)
                        if created:
                            sub_created += 1
                        channel = form.cleaned_data["channel_id"]
                        if not subscription.channels.filter(id=channel).exists():
                            subscription.channels.add(form.cleaned_data["channel_id"])
                            num_created += 1
                messages.success(
                    request,
                    _(
                        f"Subscribed to event {obj}. Created {sub_created} subscriptions and"
                        f" registered {num_created} channels"
                    ),
                )
                return HttpResponseRedirect(url)
        else:
            if (subscriptions := Subscription.objects.filter(address__user=request.user, event=obj)).exists():
                registered_addresses = subscriptions.first().channels.values_list("id", flat=True)
            else:
                registered_addresses = []
            context["formset"] = EventSubscribeFormSet(
                initial=[
                    {
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                    }
                    for channel in obj.channels.all()
                ],
                form_kwargs={"channel_choices": channel_choices, "registered_addresses": registered_addresses},
            )
        return TemplateResponse(request, "admin/event/subscribe_event.html", context)

    @button(visible=lambda s: s.context["original"].channels.exists(), html_attrs={"style": "background-color:green"})
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
