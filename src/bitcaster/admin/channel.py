import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import AdminForm
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Channel

from ..dispatchers.base import Payload
from .base import BaseAdmin
from .mixins import LockMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import AnyResponse

logger = logging.getLogger(__name__)


class ChannelChangeForm(forms.ModelForm["Channel"]):
    class Meta:
        model = Channel
        # exclude = ('config', 'dispatcher', 'locked')
        exclude = ("config", "locked")


class ChannelAddForm(forms.ModelForm["Channel"]):
    class Meta:
        model = Channel
        exclude = ("config", "locked")


class ChannelTestForm(forms.Form):
    recipient = forms.CharField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class ChannelAdmin(BaseAdmin, LockMixin, admin.ModelAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "application", "dispatcher_", "active", "locked")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application", LinkedAutoCompleteFilter.factory(parent="organization")),
        "active",
        "locked",
    )
    autocomplete_fields = ("organization", "application")
    form = ChannelChangeForm
    add_form = ChannelAddForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Channel]:
        return super().get_queryset(request).select_related("application__project__organization")

    def get_form(
        self, request: "HttpRequest", obj: "Optional[Channel]" = None, change: bool = False, **kwargs: Any
    ) -> "type[forms.ModelForm[Channel]]":
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, change, **defaults)

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[AnyModel]" = None) -> "_ListOrTuple[str]":
        return []

    @button()
    def events(self, request: "HttpRequest", pk: str) -> "Union[AnyResponse,HttpResponseRedirect]":
        base_url = reverse("admin:bitcaster_event_changelist")
        url = f"{base_url}?channels__exact={pk}"
        return HttpResponseRedirect(url)

    @button()
    def configure(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj = self.get_object(request, pk)
        context = self.get_common_context(request, pk, title=_("Configure channel"))
        form_class = obj.dispatcher.config_class
        if request.method == "POST":
            config_form = form_class(request.POST)
            if config_form.is_valid():
                obj.config = config_form.cleaned_data
                obj.save()
                self.message_user(request, "Configured channel {}".format(obj.name))
        else:
            config_form = form_class(initial={k: v for k, v in obj.config.items() if k in form_class.declared_fields})
        fs = (("", {"fields": form_class.declared_fields}),)
        context["admin_form"] = AdminForm(config_form, fs, {})  # type: ignore[arg-type]
        return TemplateResponse(request, "admin/channel/configure.html", context)

    @button()
    def test(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        from bitcaster.models import Event

        obj = self.get_object(request, pk)
        context = self.get_common_context(request, pk, title=_("Test channel"))
        if request.method == "POST":
            config_form = ChannelTestForm(request.POST)
            if config_form.is_valid():
                recipient = config_form.cleaned_data["recipient"]
                payload = Payload(
                    config_form.cleaned_data["message"], event=Event(), subject=config_form.cleaned_data["subject"]
                )
                obj.dispatcher.send(recipient, payload)
                self.message_user(request, "Message sent to {} via {}".format(recipient, obj.name))
        else:
            config_form = ChannelTestForm(initial=obj.config)  # type: ignore

        context["form"] = config_form
        return TemplateResponse(request, "admin/channel/test.html", context)

    def dispatcher_(self, obj: Channel) -> str:
        return obj.dispatcher.name
