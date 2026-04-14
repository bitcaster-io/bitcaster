import logging
from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:  # pragma: no cover
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
            _("Recipients filters"),
            {
                "classes": ["tab"],
                "description": _(
                    "Defines who should receive the notification. You can use a static distribution list, "
                    "dynamic rules based on user attributes, or external filters passed via API."
                ),
                "fields": [
                    "active",
                    "policy",
                    "distribution",
                    "recipients_filter",
                    "context_filter",
                ],
            },
        ),
        (
            _("Notification filter"),
            {
                "classes": ["tab"],
                "description": _(
                    "Defines when this notification should be triggered. Use JMESPath syntax to match "
                    "the incoming event data. If the data does not match, the notification is skipped."
                ),
                "fields": ["payload_filter"],
            },
        ),
        (
            _("Extra context"),
            {
                "classes": ["tab"],
                "description": _(
                    "Additional static variables that will be available in the message templates. "
                    "Use this to define notification-specific data like support emails or custom labels."
                ),
                "fields": ["extra_context"],
            },
        ),
    )

    conditional_fields = {
        "distribution": "active == true && policy == 1",
        "context_filter": "active == true && policy == 2",
        "recipients_filter": "active == true && policy == 4",
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

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        ret = super().get_changeform_initial_data(request)
        ret.setdefault("recipients_filter", {"include": [], "exclude": []})
        return ret

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
