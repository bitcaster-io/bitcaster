import logging
from typing import Any, Union

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

from bitcaster.models import Event, Subscription, User, Validation

from .base import BUTTON_COLOR_ACTION, BUTTON_COLOR_LINK, BaseAdmin
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
    validation = forms.ChoiceField(label=_("Address"), choices=(("", "--"),), required=False)

    def __init__(self, user: User, event: Event, **kwargs: Any):
        validation_choices = [
            [id, f"{address} ({channel})"]
            for id, address, channel in Validation.objects.filter(address__user=user, validated=True).values_list(
                "id", "address__name", "channel__name"
            )
        ]
        initial = kwargs.get("initial")
        if initial:
            channel_id = initial["channel_id"]

            validation_address = Subscription.objects.filter(event=event, validation__channel_id=channel_id).first()
            if validation_address:
                initial["validation"] = validation_address.id
        super().__init__(**kwargs)
        self.fields["validation"].choices = list(self.fields["validation"].choices) + list(validation_choices)


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

    @button(html_attrs={"style": f"background-color:{BUTTON_COLOR_LINK}"})
    def subscriptions(self, request: "HttpRequest", pk: str) -> "Union[HttpResponseRedirect]":
        obj = self.get_object(request, pk)
        base_url = reverse("admin:bitcaster_subscription_changelist")
        url = (
            f"{base_url}?event__exact={pk}"
            f"&event__application__project__organization__exact={obj.application.project.organization.id}"
            f"&event__application__project__exact={obj.application.project.id}"
            f"&event__application__exact={obj.application.id}"
        )
        return HttpResponseRedirect(url)

    @button(
        visible=lambda s: s.context["original"].channels.exists(),
        html_attrs={"style": f"background-color:{BUTTON_COLOR_ACTION}"},
    )
    def subscribe(self, request: HttpRequest, pk: str) -> Union[HttpResponseRedirect, HttpResponse]:
        obj = self.get_object(request, pk)
        context = self.get_common_context(request, pk, title=_(f"Subscribe to event {obj}"))

        if request.method == "POST":
            context["formset"] = formset = EventSubscribeFormSet(
                data=request.POST,
                form_kwargs={"user": request.user, "event": obj},
            )
            if formset.is_valid():
                sub_created = 0
                url = reverse("admin:bitcaster_event_change", args=[obj.id])
                for form in formset:
                    if validation_id := form.cleaned_data["validation"]:
                        subscription, created = Subscription.objects.get_or_create(
                            validation_id=validation_id, event=obj
                        )
                        if created:
                            sub_created += 1
                messages.success(
                    request,
                    _(f"Subscribed to event {obj}. Created {sub_created} subscriptions"),
                )
                return HttpResponseRedirect(url)
        else:
            context["formset"] = EventSubscribeFormSet(
                initial=[
                    {
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                    }
                    for channel in obj.channels.all()
                ],
                form_kwargs={"user": request.user, "event": obj},
            )
        return TemplateResponse(request, "admin/event/subscribe_event.html", context)

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
