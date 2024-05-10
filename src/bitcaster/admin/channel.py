import logging
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from constance import config
from django import forms
from django.contrib.admin.helpers import AdminForm
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from reversion.admin import VersionAdmin

from bitcaster.models import Channel, User

from ..dispatchers.base import MessageProtocol, Payload
from ..forms.channel import ChannelAddForm, ChannelChangeForm
from .base import BaseAdmin, ButtonColor
from .mixins import LockMixin, TwoStepCreateMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import AnyResponse, AuthHttpRequest

logger = logging.getLogger(__name__)


class ChannelTestForm(forms.Form):
    recipient = forms.CharField()
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)


class ChannelAdmin(BaseAdmin, TwoStepCreateMixin[Channel], LockMixin[Channel], VersionAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "project", "application", "dispatcher_", "active", "locked")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="project")),
        "active",
        "locked",
        ("dispatcher", ChoicesFieldComboFilter),
    )
    autocomplete_fields = ("organization", "application")
    change_list_template = "admin/reversion_change_list.html"
    form = ChannelChangeForm
    add_form = ChannelAddForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Channel]:
        return super().get_queryset(request).select_related("application", "project", "organization")

    def get_form(
        self, request: "HttpRequest", obj: "Optional[Channel]" = None, change: bool = False, **kwargs: Any
    ) -> "type[forms.ModelForm[Channel]]":
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, change, **defaults)

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[AnyModel]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk == config.SYSTEM_EMAIL_CHANNEL:
            return ["name", "organization", "project", "application"]
        return []

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "name": "Channel-1",
            **super().get_changeform_initial_data(request),
        }

    @button(html_attrs={"style": f"background-color:{ButtonColor.ACTION}"})
    def events(self, request: "HttpRequest", pk: str) -> "Union[AnyResponse,HttpResponseRedirect]":
        base_url = reverse("admin:bitcaster_event_changelist")
        url = f"{base_url}?channels__exact={pk}"
        return HttpResponseRedirect(url)

    @button(html_attrs={"style": f"background-color:{ButtonColor.ACTION}"})
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
                return HttpResponseRedirect("..")
        else:
            config_form = form_class(initial={k: v for k, v in obj.config.items() if k in form_class.declared_fields})
        fs = (("", {"fields": form_class.declared_fields}),)
        context["admin_form"] = AdminForm(config_form, fs, {})  # type: ignore[arg-type]
        return TemplateResponse(request, "admin/channel/configure.html", context)

    @button()
    def test(self, request: "AuthHttpRequest", pk: str) -> "HttpResponse":
        from bitcaster.models import Event

        ch: Channel = cast(Channel, self.get_object(request, pk))
        user: User = request.user
        context = self.get_common_context(request, pk, title=_("Test channel"))
        if request.method == "POST":
            config_form = ChannelTestForm(request.POST)
            if config_form.is_valid():
                recipient = config_form.cleaned_data["recipient"]
                payload = Payload(
                    config_form.cleaned_data["message"], event=Event(), subject=config_form.cleaned_data["subject"]
                )
                try:
                    ch.dispatcher.send(recipient, payload)
                except Exception as e:
                    self.message_error_to_user(request, e)
                self.message_user(request, "Message sent to {} via {}".format(recipient, ch.name))
        else:
            config_form = ChannelTestForm(
                initial={
                    "recipient": user.get_address_for_protocol(MessageProtocol[ch.protocol]),
                    "subject": "[TEST] Subject",
                    "message": "aaa",
                }
            )

        context["recipient"] = user.get_address_for_protocol(MessageProtocol[ch.protocol])
        context["form"] = config_form
        return TemplateResponse(request, "admin/channel/test.html", context)

    def dispatcher_(self, obj: Channel) -> str:
        return obj.dispatcher.name
