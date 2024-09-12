import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from bitcaster.forms.application import ApplicationChangeForm
from bitcaster.models import Application

from ..constants import Bitcaster
from ..state import state
from ..utils.django import url_related
from .base import BaseAdmin, ButtonColor
from .mixins import LockMixinAdmin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class ApplicationAdmin(BaseAdmin, LockMixinAdmin[Application], admin.ModelAdmin[Application]):
    search_fields = ("name",)
    list_display = ("name", "project", "organization", "active", "locked")
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
        "active",
        "locked",
    )
    # autocomplete_fields = ("project", "owner")
    readonly_fields = ["locked"]
    form = ApplicationChangeForm

    def has_add_permission(self, request: HttpRequest) -> bool:
        from bitcaster.models import Project

        return super().has_add_permission(request) and Project.objects.local().count() > 0

    def get_queryset(self, request: HttpRequest) -> QuerySet[Application]:
        return super().get_queryset(request).select_related("project", "project__organization", "owner")

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Application] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.organization.name == Bitcaster.ORGANIZATION:
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

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def events(self, request: HttpRequest, pk: str) -> "HttpResponse":
        ctx = self.get_common_context(request, pk, title=_("Events"))
        return TemplateResponse(request, "admin/application/events.html", ctx)

    @button(
        visible=lambda s: s.context["original"].project.organization.name != Bitcaster.ORGANIZATION,
        html_attrs={"class": ButtonColor.ACTION.value},
    )
    def add_event(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Event

        return HttpResponseRedirect(url_related(Event, op="add", application=pk))
