import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from constance import config
from django import forms
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.forms.unfold import UnfoldAdminForm
from bitcaster.models import Assignment, Channel, User

from ..dispatchers.base import Payload
from ..forms.channel import ChannelChangeForm
from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor
from .filters import ChannelTypeFilter
from .mixins import LockMixinAdmin, TwoStepCreateMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

    from bitcaster.types.django import AnyModel_co
    from bitcaster.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class ChannelTestForm(forms.Form):
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)


class ManagementForm(forms.Form):
    prefix = "mng"
    current_step = forms.IntegerField()


class ChannelAdmin(BaseAdmin, TwoStepCreateMixin[Channel], LockMixinAdmin[Channel], BitcasterModelAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "project", "dispatcher_", "active", "locked", "protocol")
    list_filter = (
        ChannelTypeFilter,
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        "protocol",
        "active",
        "locked",
    )
    form = ChannelChangeForm

    def dispatcher_(self, obj: Channel) -> str:
        return str(obj.dispatcher)

    def get_queryset(self, request: "HttpRequest") -> QuerySet[Channel]:
        return super().get_queryset(request).select_related("project", "organization")

    def get_readonly_fields(self, request: "HttpRequest", obj: "AnyModel_co | None" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk == config.SYSTEM_EMAIL_CHANNEL:
            return ["name", "organization", "project", "parent", "protocol", "locked"]
        if obj and obj.pk:
            return ["parent", "organization", "protocol", "locked", "project"]
        return []

    @link(change_form=True, change_list=False)
    def events(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_event_changelist")
        ch: Channel = button.context["original"]
        if ch:
            button.href = f"{url}?channels__exact={ch.pk}"

    @link(change_form=True, change_list=False)
    def assignments(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_assignment_changelist")
        ch: Channel = button.context["original"]
        if ch:
            button.href = f"{url}?channel__id__exact={ch.pk}"

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def configure(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj: "Channel" = self.get_object_or_404(request, pk)
        context = self.get_common_context(request, pk, action_title=_("Configure channel"))
        form_class = obj.dispatcher.config_class
        if form_class:
            if request.method == "POST":
                config_form = form_class(request.POST)
                if config_form.is_valid():
                    config_form.save(obj)
                    self.message_user(request, f"Configured channel {obj.name}")
                    return HttpResponseRedirect(reverse("admin:bitcaster_channel_change", args=(obj.pk,)))
            else:
                initial = {k: v for k, v in obj.config.items() if k in form_class.declared_fields}
                for k, v in obj.dispatcher.default_config.items():
                    if k not in initial:
                        initial[k] = v

                config_form = form_class(initial=initial)
            fs = (("", {"fields": form_class.declared_fields}),)
            context["adminform"] = UnfoldAdminForm(config_form, fs, {}, model_admin=self)  # type: ignore[arg-type]
            context["extra_config_info"] = obj.dispatcher.get_extra_config_info()
        return TemplateResponse(request, "bitcaster/admin/channel/configure.html", context)

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def test(self, request: "AuthHttpRequest", pk: str) -> "HttpResponse":
        from bitcaster.models import Event

        ch: Channel = self.get_object_or_404(request, pk)
        user: User = request.user
        assignment: Assignment | None = user.get_assignment_for_channel(ch)
        context = self.get_common_context(request, pk, action_title=_("Test channel"))
        if request.method == "POST":
            config_form = ChannelTestForm(request.POST)
            if config_form.is_valid():
                recipient = str(assignment.address.value)
                payload = Payload(
                    message=config_form.cleaned_data["message"],
                    event=Event(),
                    subject=config_form.cleaned_data["subject"],
                )
                try:
                    ch.dispatcher.send(recipient, payload, assignment=assignment)
                    self.message_user(request, f"Message sent to {recipient} via {ch.name}")
                    return HttpResponseRedirect(".")
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)
        else:
            config_form = ChannelTestForm(
                initial={
                    "subject": f"[TEST Channel] {ch}",
                    "message": f"Test message sent on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
                }
            )
        context["assignment"] = assignment
        fs = (("", {"fields": ChannelTestForm.declared_fields}),)
        context["adminform"] = UnfoldAdminForm(config_form, fs, {})
        return TemplateResponse(request, "bitcaster/admin/channel/test.html", context)
