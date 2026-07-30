from typing import TYPE_CHECKING, Any, cast

import logging

from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import LinkedAutoCompleteFilter

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import bitcaster
from bitcaster.forms.application import ApplicationAdvancedConfigForm, ApplicationChangeForm
from bitcaster.forms.unfold import UnfoldAdminForm
from bitcaster.models import Application
from bitcaster.state import state
from bitcaster.utils.django import url_related

from .base import BaseAdmin, ButtonColor
from .mixins import LockMixinAdmin

if TYPE_CHECKING:  # pragma: no cover
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class ApplicationAdmin(LockMixinAdmin[Application], BaseAdmin[Application]):
    search_fields = ("name",)
    list_display = ("name", "project", "organization", "active", "locked")
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
        "active",
        "locked",
    )
    readonly_fields = ["locked"]
    autocomplete_fields = ("owner",)
    form = ApplicationChangeForm
    change_form_template = "bitcaster/admin/application/change_form.html"
    fieldsets = (
        (
            _("General"),
            {
                "classes": ["tab"],
                "fields": [
                    "name",
                    "slug",
                    "project",
                    "owner",
                ],
            },
        ),
        (_("Events auto creation"), {"classes": ["tab"], "fields": ["auto_create_event", "auto_create_options"]}),
        (_("Status"), {"classes": ["tab"], "fields": ["active", "locked", "paused"]}),
        (_("Notification"), {"classes": ["tab"], "fields": ["from_email", "subject_prefix"]}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        from ..models import Project

        return cast("bool", super().has_add_permission(request) and Project.objects.local().count() > 0)

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet[Application], search_term: str
    ) -> tuple[QuerySet[Application], bool]:
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        project_id = request.GET.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset, use_distinct

    def get_queryset(self, request: HttpRequest) -> QuerySet[Application]:
        return super().get_queryset(request).select_related("project", "project__organization", "owner")

    def get_readonly_fields(self, request: HttpRequest, obj: Application | None = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.organization.name == bitcaster.ORGANIZATION:
            base.extend(
                [
                    "name",
                    "slug",
                    "project",
                    "active",
                ]
            )
        return base

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        from ..models import Project

        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", str(request.user.id))
        initial.setdefault("project", state.get_cookie("project"))
        initial["project"] = Project.objects.filter(pk=state.get_cookie("project")).first()
        initial.setdefault("from_email", str(request.user.email))
        return initial

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def events(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_event_changelist")
        application: Application = button.context["original"]
        # application__project__exact=4&application__exact=5
        if application:
            button.href = (
                f"{url}?application__exact={application.pk}&application__project__exact={application.project.pk}"
            )
        else:
            button.visible = False

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def notifications(self, button: StandardButton) -> None:
        url = reverse("admin:bitcaster_notification_changelist")
        application: Application = button.context["original"]
        if application:
            button.href = f"{url}?event__application__exact={application.pk}"
        else:
            button.visible = False

    @button(  # type: ignore[arg-type]
        visible=lambda s: s.context["original"].project.organization.name != bitcaster.ORGANIZATION,
        html_attrs={"class": ButtonColor.ACTION.value},
    )
    def add_event(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        from bitcaster.models import Event

        return HttpResponseRedirect(url_related(Event, op="add", application=pk))

    @button(  # type: ignore[arg-type]
        visible=lambda s: bool(s.context["original"].pk),
        html_attrs={"class": ButtonColor.ACTION.value},
    )
    def configure(self, request: HttpRequest, pk: str) -> HttpResponse:
        obj: Application = self.get_object_or_404(request, pk)
        context = self.get_common_context(request, pk, action_title=_("Advanced configuration"))
        if request.method == "POST":
            config_form = ApplicationAdvancedConfigForm(request.POST)
            if config_form.is_valid():  # pragma: no branch
                obj.advanced_configuration = config_form.cleaned_data
                obj.save()
                self.message_user(request, str(_("Advanced configuration saved.")))
                return HttpResponseRedirect(reverse("admin:bitcaster_application_change", args=(obj.pk,)))
        else:
            initial = {
                k: v
                for k, v in obj.advanced_configuration.items()
                if k in ApplicationAdvancedConfigForm.declared_fields
            }
            config_form = ApplicationAdvancedConfigForm(initial=initial)

        fs = [("", {"fields": list(ApplicationAdvancedConfigForm.declared_fields.keys())})]
        context["adminform"] = UnfoldAdminForm(config_form, fs, {}, model_admin=self)
        return TemplateResponse(request, "bitcaster/admin/application/configure.html", context)
