import logging
from typing import TYPE_CHECKING, Any, Sequence

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Assignment, Event

from ..constants import bitcaster
from ..forms.event import EventChangeForm
from ..state import state
from .base import BaseAdmin, ButtonColor
from .message import Message
from .mixins import LockMixinAdmin, TwoStepCreateMixin

if TYPE_CHECKING:
    from django.contrib.admin.options import _FieldsetSpec
    from django.http import HttpResponse
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class MessageInline(admin.TabularInline[Message, Event]):
    model = Message
    extra = 0
    fields = [
        "name",
    ]
    show_change_link = True


class EventTestForm(forms.Form):
    assignment = forms.ModelChoiceField(queryset=Assignment.objects.none())


class EventAdmin(BaseAdmin, TwoStepCreateMixin[Event], LockMixinAdmin[Event], admin.ModelAdmin[Event]):
    search_fields = ("name",)
    list_display = ("name", "application", "active", "locked")
    list_filter = (
        # ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
        ("channels", AutoCompleteFilter),
        ("notifications__distribution", LinkedAutoCompleteFilter.factory(parent=None)),
        ("notifications__distribution__recipients__address__user", LinkedAutoCompleteFilter.factory(parent=None)),
        "active",
        "locked",
    )
    autocomplete_fields = ("application",)
    filter_horizontal = ("channels",)
    form = EventChangeForm
    save_as_continue = False
    save_as = False
    _fieldsets: "_FieldsetSpec" = [
        (
            None,
            {
                "fields": (
                    ("name", "slug"),
                    ("description",),
                    ("active", "newsletter", "occurrence_retention"),
                    # ("channels",)
                )
            },
        ),
        (
            "Channels",
            {
                "fields": ["channels"],
            },
        ),
    ]
    change_form_template = None

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/js/jquery.init.js", "bitcaster/js/copy.js"]

    def get_fieldsets(self, request: HttpRequest, obj: Event | None = None) -> "_FieldsetSpec":
        if obj:
            return self._fieldsets
        return [(None, {"fields": self.get_fields(request, obj)})]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Event]) -> None:
        queryset.exclude(application__project__organization__name=bitcaster.ORGANIZATION).delete()

    def get_deleted_objects(
        self, objs: QuerySet[Event] | Sequence[Event], request: HttpRequest
    ) -> tuple[list[Any] | Any, dict[str, Any] | Any, set[Any] | Any, list[Any] | Any]:
        if isinstance(objs, QuerySet):
            objs = objs.exclude(application__project__organization__name=bitcaster.ORGANIZATION)
            to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        elif objs[0].application.project.organization.name == bitcaster.ORGANIZATION:
            to_delete, model_count, perms_needed, protected = [], {}, set(), objs  # type: ignore[assignment]
        else:
            to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        return to_delete, model_count, perms_needed, protected

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", request.user.id)
        initial.setdefault("organization", state.get_cookie("organization"))
        initial.setdefault("from_email", request.user.email)
        return initial

    def get_readonly_fields(self, request: "HttpRequest", obj: "Event | None" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["application", "slug", "name"]
        return []

    def get_fields(self, request: HttpRequest, obj: Event | None = None) -> Sequence[str | Sequence[str]]:
        form = self._get_form_for_get_fields(request, obj)
        return [*self.get_readonly_fields(request, obj), *form.base_fields]

    def get_exclude(self, request: "HttpRequest", obj: "Event | None" = None) -> "_ListOrTuple[str]":
        if obj is None:
            return ["channels", "locked"]
        return ["locked"]

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def trigger_event(self, request: HttpRequest, pk: str) -> "HttpResponse":
        from bitcaster.models import Occurrence

        def get_form(*args: Any, **kwargs: Any) -> EventTestForm:
            frm = EventTestForm(*args, **kwargs)
            frm.fields["assignment"].queryset = Assignment.objects.filter(
                distributionlist__recipients__address__user=request.user
            ).distinct()
            return frm

        context = self.get_common_context(request, pk, title=_("Trigger Event"))
        evt: Event | None = self.get_object(request, pk)
        if request.method == "POST":
            config_form = get_form(request.POST)
            if config_form.is_valid():
                try:
                    o: Occurrence = evt.trigger(
                        context={},
                        options={
                            "limit_to": [config_form.cleaned_data["assignment"].address.value],
                            "channels": [config_form.cleaned_data["assignment"].channel.pk],
                        },
                    )
                    o.process()
                    self.message_user(request, f"Sent {o.data}", messages.SUCCESS)
                    return HttpResponseRedirect(".")
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)
        else:
            config_form = get_form(
                initial={
                    "subject": "[TEST] Subject",
                    "message": "aaa",
                }
            )
        context["form"] = config_form
        return TemplateResponse(request, "admin/bitcaster/event/test_event.html", context)

    #
    # @button(html_attrs={"class": ButtonColor.LINK.value})
    # def notifications(self, request: HttpRequest, pk: str) -> "HttpResponse":
    #     ctx = self.get_common_context(request, pk, title=_("Notifications"))
    #     # ctx[""]
    #     return TemplateResponse(request, "admin/bitcaster/event/notifications.html", ctx)

    @link(change_form=True, change_list=False)
    def notifications(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_notification_changelist")
        event: Event = button.context["original"]
        button.href = f"{url}?event__exact={event.pk}&event__application__exact={event.application.pk}"
