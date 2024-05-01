import logging
from typing import Any, Optional

from admin_extra_buttons.decorators import button, view
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django import forms
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import Context, Template
from django.template.response import TemplateResponse
from django.utils import timezone
from reversion.admin import VersionAdmin

from bitcaster.models import Message, Notification, Occurrence

from ..forms.message import MessageChangeForm, MessageCreationForm, MessageEditForm
from .base import BaseAdmin

logger = logging.getLogger(__name__)


class MessageAdmin(BaseAdmin, VersionAdmin[Message]):
    search_fields = ("name",)
    list_display = ("name", "channel", "event", "notification")
    list_filter = (
        ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
        ("event", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
    )
    autocomplete_fields = ("channel", "event", "notification")
    change_form_template = "admin/message/change_form.html"
    form = MessageChangeForm
    add_form = MessageCreationForm

    def get_form(self, request: HttpRequest, obj: Optional["Message"] = None, **kwargs: dict[str, Any]) -> forms.Form:
        defaults: dict[str, Any] = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Message]:
        return super().get_queryset(request).select_related("channel", "event", "notification")

    def get_dummy_source(self, obj: Message) -> tuple[Occurrence, Notification]:
        from bitcaster.models import Event, Notification, Occurrence

        event = obj.event if obj.event else Event(name="Sample Event")
        no = Notification(name="Sample Notification", event=event)
        oc = Occurrence(event=event, timestamp=timezone.now())
        return oc, no

    @view()
    def render(self, request: HttpRequest, pk: str) -> "HttpResponse":
        form = MessageEditForm(request.POST)
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

    @button()
    def edit(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk)
        obj = context["original"]
        oc, no = self.get_dummy_source(obj)
        message_context = no.get_context(oc.get_context())

        if request.method == "POST":
            form = MessageEditForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("..")
        else:
            form = MessageEditForm(
                initial={
                    "context": {k: "<sys>" for k, __ in message_context.items()},
                    "content": "\n".join([f"{k}: {{{{{k}}}}}" for k in message_context.keys()]),
                    "html_content": "".join([f"<div>{k}: {{{{{k}}}}}</div>" for k in message_context.keys()]),
                    "subject": "Subject for {{ event }}",
                },
                instance=obj,
            )
        context["form"] = form
        return TemplateResponse(request, "admin/message/edit.html", context)
