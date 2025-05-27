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
from django.utils.translation import gettext as _
from reversion.admin import VersionAdmin

from bitcaster.models import (
    Application,
    Event,
    Message,
    Notification,
    Occurrence,
    Organization,
    Project,
)

from ..dispatchers.base import Dispatcher, Payload
from ..forms.message import (
    MessageChangeForm,
    MessageCreationForm,
    MessageEditForm,
    MessageRenderForm,
)
from ..utils.shortcuts import render_string
from .base import BaseAdmin, ButtonColor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..types.django import JsonType
    from ..types.http import AuthHttpRequest


class MessageAdmin(BaseAdmin, VersionAdmin[Message]):
    search_fields = ("name",)
    list_display = ("name", "channel", "scope_level")
    list_filter = (
        # ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent=None)),
        ("notification", LinkedAutoCompleteFilter.factory()),
    )
    autocomplete_fields = ("channel", "event", "notification")
    change_form_template = "admin/message/change_form.html"
    change_list_template = "admin/reversion_change_list.html"
    object_history_template = "reversion/object_history.html"

    form = MessageChangeForm
    add_form = MessageCreationForm

    def scope_level(self, obj: "Message") -> "Notification | Event | Application | Project | Organization":
        if obj.notification:
            return obj.notification
        if obj.event:
            return obj.event
        if obj.application:
            return obj.application
        if obj.project:
            return obj.project
        return obj.organization

    def get_queryset(self, request: HttpRequest) -> QuerySet[Message]:
        return (
            super()
            .get_queryset(request)
            .select_related("channel", "application", "project", "channel__organization", "event", "notification")
        )

    def get_form(self, request: HttpRequest, obj: Optional["Message"] = None, **kwargs: dict[str, Any]) -> forms.Form:
        defaults: dict[str, Any] = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_dummy_source(self, obj: Message) -> tuple[Occurrence, Notification]:
        from bitcaster.models import Event, Notification, Occurrence

        event = obj.event if obj.event else Event(name="Sample Event")
        no = Notification(name="Sample Notification", event=event)
        oc = Occurrence(event=event, timestamp=timezone.now())
        return oc, no

    @view()
    def render(self, request: HttpRequest, pk: str) -> "HttpResponse":
        form = MessageRenderForm(request.POST)
        msg: Message = self.get_object(request, pk)
        oc, no = self.get_dummy_source(msg)
        message_context = no.get_context(oc.get_context())

        ct = "text/html"
        if form.is_valid():
            tpl = Template(form.cleaned_data["content"])
            ct = form.cleaned_data["content_type"]
            try:
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
        form = MessageEditForm(request.POST)
        msg: Message = self.get_object(request, pk)
        dispatcher: Dispatcher = msg.channel.dispatcher
        # oc, no = self.get_dummy_source(msg)
        ret: "JsonType"
        if form.is_valid():
            ctx = {**form.cleaned_data["context"], "event": msg.event}
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
        context = self.get_common_context(request, pk)
        obj = context["original"]
        oc, no = self.get_dummy_source(obj)
        message_context = no.get_context(oc.get_context())

        if request.method == "POST":
            form = MessageEditForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                self.message_user(request, _("Message Template updated successfully "))
                return HttpResponseRedirect("..")
        else:
            form = MessageEditForm(
                initial={
                    "recipient": request.user.email,
                    "context": {k: "<sys>" for k, __ in message_context.items()},
                    "subject": obj.subject if obj.subject else "Subject for {{ event }}",
                    "content": (
                        obj.content if obj.content else "\n".join([f"{k}: {{{{{k}}}}}" for k in message_context])
                    ),
                    "html_content": (
                        obj.html_content
                        if obj.html_content
                        else "".join([f"<div>{k}: {{{{{k}}}}}</div>" for k in message_context])
                    ),
                },
                instance=obj,
            )
        context["form"] = form
        return TemplateResponse(request, "admin/message/edit.html", context)

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def usage(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, title=_("Message usage"))
        msg: "Message" = context["original"]
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
        return TemplateResponse(request, "admin/message/usage.html", context)
