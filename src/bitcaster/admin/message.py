import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button, view
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django import forms
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import Context, Template
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from bitcaster.models import (
    Application,
    DistributionList,
    Event,
    MessageTemplate,
    Notification,
    Organization,
    Project,
)

from ..dispatchers.base import Dispatcher, Payload
from ..forms.message import (
    MessageTemplateChangeForm,
    MessageTemplateCloneForm,
    MessageTemplateCreationForm,
    MessageTemplateEditForm,
    MessageTemplateRenderForm,
)
from ..forms.unfold import UnfoldAdminForm
from ..utils.shortcuts import render_string
from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..types.django import JsonType
    from ..types.http import AuthHttpRequest

SAMPLE_TEXT_MESSAGE = """This is a sample message for event '{{ event }}' for the application '{{ event.application}}'.

It hs been triggered on {{timestamp|date:"Y-m-d"}} at {{timestamp|date:"H:m"}},
 and produced by the notification '{{notification}}' for the DistributionList '{{ distribution }}'


The destination address is '{{ address }}' thru the channel '{{ channel }}'

"""

SAMPLE_HTML_MESSAGE = """
<div>
This is a sample message for event: <b>{{ event }}</b> for the application <b>{{ event.application}}</b>.
</div>

<div>
It hs been triggered on {{timestamp|date:"Y-m-d"}} at {{timestamp|date:"H:m"}}.
and produced by the notification '{{notification}}' for the DistributionList '{{ distribution }}'
</div>

The destination address is {{ address }} thru the channel {{ channel }}

"""


class MessageTemplateAdmin(BaseAdmin, BitcasterModelAdmin, VersionAdmin[MessageTemplate]):
    search_fields = ("name",)
    list_display = ("name", "channel", "scope_level")
    list_filter = (
        ("channel", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent=None)),
        ("notification", LinkedAutoCompleteFilter.factory()),
    )
    autocomplete_fields = ("channel", "event", "notification")
    change_form_template = "bitcaster/admin/message/change_form.html"
    change_list_template = "admin/reversion_change_list.html"
    object_history_template = "reversion/object_history.html"

    form = MessageTemplateChangeForm
    add_form = MessageTemplateCreationForm

    def scope_level(self, obj: "MessageTemplate") -> "Notification | Event | Application | Project | Organization":
        if obj.notification:
            return obj.notification
        if obj.event:
            return obj.event
        if obj.application:
            return obj.application
        if obj.project:
            return obj.project
        return obj.organization

    def get_queryset(self, request: HttpRequest) -> QuerySet[MessageTemplate]:
        return (
            super()
            .get_queryset(request)
            .select_related("channel", "application", "project", "channel__organization", "event", "notification")
        )

    def get_form(
        self, request: HttpRequest, obj: Optional["MessageTemplate"] = None, **kwargs: dict[str, Any]
    ) -> forms.Form:
        defaults: dict[str, Any] = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_dummy_source_context(
        self, obj: MessageTemplate, extra_context: dict[str, str] | None = None
    ) -> dict[str, str]:
        from bitcaster.models import Event, Notification, Occurrence

        event = obj.event if obj.event else Event(name="Sample Event")
        dl = DistributionList(name="Sample DistributionList", project=event.application.project)
        no = Notification(name="Sample Notification", event=event, distribution=dl)
        oc = Occurrence(event=event, timestamp=timezone.now())
        return no.get_context(oc.get_context()) | (extra_context or {})

    @button()
    def clone(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, action_title="Clone")
        cloned: MessageTemplate = context["original"]
        cloned.name = f"Copy of {cloned.name}"
        cloned.pk = None
        if request.method == "POST":
            form = MessageTemplateCloneForm(request.POST, instance=cloned)
            if form.is_valid():
                form.save()
                self.message_user(request, _("Message Template updated successfully "))
                return HttpResponseRedirect("..")
        else:
            form = MessageTemplateCloneForm(instance=cloned)
        fs = (("", {"fields": MessageTemplateCloneForm.declared_fields}),)
        context["admin_form"] = UnfoldAdminForm(form, fs, {}, model_admin=self)  # type: ignore[arg-type]
        context["form"] = form
        return TemplateResponse(request, "bitcaster/admin/message/clone.html", context)

    @view()
    def render(self, request: HttpRequest, pk: str) -> "HttpResponse":
        form = MessageTemplateRenderForm(request.POST)
        msg: MessageTemplate = self.get_object(request, pk)
        message_context = self.get_dummy_source_context(msg)

        ct = "text/html"
        if form.is_valid():
            message_context |= {"channel": msg.channel.name, "address": form.cleaned_data["recipient"]}
            try:
                tpl = Template(form.cleaned_data["content"])
                ct = form.cleaned_data["content_type"]
                ctx = {**form.cleaned_data["context"], **message_context}
                res = str(tpl.render(Context(ctx)))
                if ct != "text/html":
                    res = f"<pre>{res}</pre>"
            except Exception as e:
                res = f"<!DOCTYPE HTML>{str(e)}"
        else:
            res = f"<!DOCTYPE HTML>{form.errors.as_text()}"

        return HttpResponse(res, content_type=ct)

    @view()
    def send_message(self, request: "AuthHttpRequest", pk: str) -> "HttpResponse":
        form = MessageTemplateEditForm(request.POST)
        msg: MessageTemplate = self.get_object(request, pk)
        dispatcher: Dispatcher = msg.channel.dispatcher
        ret: "JsonType"
        if form.is_valid():
            message_context = self.get_dummy_source_context(
                msg, extra_context={"channel": msg.channel.name, "address": form.cleaned_data["recipient"]}
            )
            ctx = {**form.cleaned_data["context"], **message_context}

            payload: Payload = Payload(
                subject=render_string(form.cleaned_data["subject"], ctx),
                message=render_string(form.cleaned_data["content"], ctx),
                user=request.user,
                html_message=render_string(form.cleaned_data["html_content"], ctx),
                event=Event(name="Sample Event"),
            )
            recipient = form.cleaned_data["recipient"]
            if not dispatcher.send(recipient, payload):
                ret = {"error": f"Failed to send message to {recipient}"}
            else:
                ret = {"success": "message sent"}
        else:
            ret = {"error": form.errors}

        return JsonResponse(ret)

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def edit(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, action_title="Edit")
        msg = context["original"]
        message_context = self.get_dummy_source_context(
            msg, extra_context={"channel": msg.channel.name, "address": "<sys>"}
        )

        if request.method == "POST":
            form = MessageTemplateEditForm(request.POST, instance=msg)
            if form.is_valid():
                form.save()
                self.message_user(request, _("Message Template updated successfully "))
                return HttpResponseRedirect("..")
        else:
            form = MessageTemplateEditForm(
                initial={
                    "recipient": request.user.email,
                    "context": {k: "<sys>" for k, __ in message_context.items()},
                    "subject": msg.subject if msg.subject else "Subject for {{ event }}",
                    "content": (msg.content if msg.content else SAMPLE_TEXT_MESSAGE),
                    "html_content": (msg.html_content if msg.html_content else SAMPLE_HTML_MESSAGE),
                },
                instance=msg,
            )
        context["form"] = form
        return TemplateResponse(request, "bitcaster/admin/message/edit.html", context)

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def usage(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, action_title=_("Message usage"))
        msg: "MessageTemplate" = context["original"]
        usage: list[Any] = []
        level = ""
        if msg.notification:
            usage.extend([msg.notification])
            level = str(Notification._meta.verbose_name)
        elif msg.event:
            usage.extend(Event.objects.filter(messages=msg))
            usage.extend(msg.event.notifications.all())
            level = str(Event._meta.verbose_name)
        elif msg.application:
            usage.extend([msg.application])
            usage.extend(Application.objects.filter(events__messages=msg))
            usage.extend(Event.objects.filter(application=msg.application))
            usage.extend(Notification.objects.filter(event__application=msg.application))
            level = str(Application._meta.verbose_name)
        elif msg.project:
            usage.extend([msg.project])
            usage.extend(Application.objects.filter(events__messages=msg))
            usage.extend(Event.objects.filter(application=msg.application))
            usage.extend(Notification.objects.filter(event__application=msg.application))

            level = str(Project._meta.verbose_name)
        else:
            usage.extend([msg.organization])
            usage.extend(Application.objects.filter(events__messages=msg))
            usage.extend(Event.objects.filter(application=msg.application))
            usage.extend(Notification.objects.filter(event__application=msg.application))

            level = str(Organization._meta.verbose_name)

        context["usage"] = usage
        context["level"] = level
        return TemplateResponse(request, "bitcaster/admin/message/usage.html", context)
