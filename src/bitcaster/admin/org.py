import logging
from typing import TYPE_CHECKING, Optional

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from bitcaster.models import Application, Channel, Organization, Project

from ..state import state
from ..utils.django import url_related
from .base import BUTTON_COLOR_LINK, BaseAdmin
from .mixins import LockMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


logger = logging.getLogger(__name__)


class OrganisationAdmin(BaseAdmin, admin.ModelAdmin[Organization]):
    search_fields = ("name",)
    list_display = ("name", "from_email", "subject_prefix")

    @button(html_attrs={"style": f"background-color:{BUTTON_COLOR_LINK}"})
    def projects(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponseRedirect(url_related(Project, organization__exact=pk))

    @button(html_attrs={"style": f"background-color:{BUTTON_COLOR_LINK}"})
    def channels(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponseRedirect(url_related(Channel, organization__exact=pk))

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Application] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name.lower() == "os4d":
            base.extend(["name", "slug"])
        return base

    def get_changeform_initial_data(self, request):
        return {
            "owner": request.user.id,
        }


class ProjectAdmin(BaseAdmin, LockMixin, admin.ModelAdmin[Project]):
    search_fields = ("name",)
    list_display = ("name", "organization")
    list_filter = (("organization", AutoCompleteFilter),)
    autocomplete_fields = ("organization",)
    exclude = ("locked",)

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Project] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name.lower() == "bitcaster":
            base.extend(["name", "slug", "organization"])
        return base

    def get_changeform_initial_data(self, request):
        return {
            "owner": request.user.id,
            "organization": state.get_cookie("organization"),
        }


class ApplicationAdmin(BaseAdmin, LockMixin, admin.ModelAdmin[Application]):
    search_fields = ("name",)
    list_display = ("name",)
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
    autocomplete_fields = ("project", "owner")
    readonly_fields = ["locked"]

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Application] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name.lower() == "bitcaster":
            base.extend(
                [
                    "name",
                    "slug",
                    "project",
                    "active",
                ]
            )
        return base

    def get_changeform_initial_data(self, request):
        return {
            "owner": request.user.id,
            "project": state.get_cookie("project"),
        }
