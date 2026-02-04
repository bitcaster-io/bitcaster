import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_ace import AceWidget
from jsoneditor.forms import JSONEditor

from ..forms.message import NotificationTemplateCreateForm
from ..forms.notification import NotificationForm
from ..utils.django import admin_toggle_bool_action
from ..utils.filtering import schema
from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor

if TYPE_CHECKING:
    from bitcaster.models import Notification

logger = logging.getLogger(__name__)


class NotificationAdmin(BaseAdmin, BitcasterModelAdmin["Notification"]):
    search_fields = ("name",)
    list_display = ("name", "event", "application", "distribution", "active")
    list_filter = (
        "active",
        ("event__application", LinkedAutoCompleteFilter.factory(parent=None)),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        ("distribution__recipients__address__user", LinkedAutoCompleteFilter.factory(parent=None)),
    )
    autocomplete_fields = ("event", "distribution")
    form = NotificationForm
    add_fieldsets = (
        (
            _("General"),
            {
                "classes": ["tab"],
                "fields": ["name", "event", "environments"],
            },
        ),
    )
    fieldsets = (
        (_("General"), {"classes": ["tab"], "fields": ["name", "event", "environments"]}),
        (
            _("Distribution"),
            {
                "classes": ["tab"],
                "fields": [
                    "active",
                    "external_filtering",
                    "dynamic",
                    "distribution",
                    "recipients_filter",
                ],
            },
        ),
        (_("Extra context"), {"classes": ["tab"], "fields": ["extra_context"]}),
    )
    conditional_fields = {
        "distribution": "active == true && (dynamic == false && external_filtering == false)",
        "external_filtering": "active == true && (dynamic == false)",
        "dynamic": "active == true && (external_filtering == false)",
        "recipients_filter": "active == true && dynamic == true",
    }
    actions = ["toggle_active"]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "recipients_filter":
            field.widget = JSONEditor(jsonschema=schema)
        elif db_field.name == "extra_context":
            field.widget = JSONEditor()
        elif db_field.name == "payload_filter":
            field.widget = AceWidget(mode="yaml")
        return field

    def get_queryset(self, request: HttpRequest) -> QuerySet["Notification"]:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "event",
                "event__application",
                "event__application__project",
                "event__application__project__organization",
                "distribution",
            )
        )

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(
            reverse(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                args=[obj.pk],
            )
        )

    def toggle_active(self, request, queryset):
        admin_toggle_bool_action(request, queryset, "active")

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def messages(self, request: HttpRequest, pk: str) -> HttpResponse:
        status_code = 200
        ctx = self.get_common_context(request, pk, title=_("Messages"))
        notification: "Notification" = ctx["original"]
        if request.method == "POST":
            form = NotificationTemplateCreateForm(request.POST, notification=notification)
            if form.is_valid():
                msg = notification.create_message(name=form.cleaned_data["name"], channel=form.cleaned_data["channel"])
                ctx["message_created"] = msg
            else:
                status_code = 400
        else:
            form = NotificationTemplateCreateForm(notification=notification)
        ctx["message_templates"] = notification.messages.filter()
        ctx["form"] = form
        return TemplateResponse(request, "bitcaster/admin/notification/messages.html", ctx, status=status_code)
