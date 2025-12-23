import logging
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from bitcaster.forms.application import ApplicationChangeForm
from bitcaster.models import Application

from ..constants import bitcaster
from ..state import state
from ..utils.django import url_related
from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor
from .mixins import LockMixinAdmin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class ApplicationAdmin(BaseAdmin, LockMixinAdmin[Application], BitcasterModelAdmin[Application]):
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

    def has_add_permission(self, request: HttpRequest) -> bool:
        from bitcaster.models import Project

        return super().has_add_permission(request) and Project.objects.local().count() > 0

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
        from bitcaster.models import Project

        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", request.user.id)
        initial.setdefault("project", state.get_cookie("project"))
        initial["project"] = Project.objects.filter(pk=state.get_cookie("project")).first()
        initial.setdefault("from_email", request.user.email)
        return initial

    @link(change_form=True, change_list=False)
    def events(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_event_changelist")
        application: Application = button.context["original"]
        # application__project__exact=4&application__exact=5
        if application:
            button.href = (
                f"{url}?application__exact={application.pk}&application__project__exact={application.project.pk}"
            )
        else:
            button.visible = False

    @link(change_form=True, change_list=False)
    def notifications(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_notification_changelist")
        application: Application = button.context["original"]
        if application:
            button.href = f"{url}?event__application__exact={application.pk}"
        else:
            button.visible = False

    @button(
        visible=lambda s: s.context["original"].project.organization.name != bitcaster.ORGANIZATION,
        html_attrs={"class": ButtonColor.ACTION.value},
    )
    def add_event(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Event

        return HttpResponseRedirect(url_related(Event, op="add", application=pk))
