import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect

from bitcaster.models import Project

from ..constants import Bitcaster
from ..forms.project import ProjectChangeForm
from ..state import state
from ..utils.django import url_related
from .base import BaseAdmin, ButtonColor
from .mixins import LockMixinAdmin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


logger = logging.getLogger(__name__)


class ProjectAdmin(BaseAdmin, LockMixinAdmin[Project], admin.ModelAdmin[Project]):
    search_fields = ("name",)
    list_display = ("name", "organization", "environments")
    list_filter = (
        ("organization", AutoCompleteFilter),
        # ("environments", ChoiceFilter),
    )
    autocomplete_fields = ("organization", "owner")
    exclude = ("locked",)
    form = ProjectChangeForm

    # def add_view(self, request, form_url="", extra_context=None):
    #     return super().add_view(request, form_url, extra_context)

    @button(html_attrs={"style": f"background-color:{ButtonColor.LINK}"})
    def add_application(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Application

        return HttpResponseRedirect(url_related(Application, op="add", projecc=pk))

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Project] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.organization.name == Bitcaster.ORGANIZATION:
            base.extend(["name", "slug", "organization"])
        return base

    def has_add_permission(self, request: HttpRequest, obj: Optional[Project] = None) -> bool:
        return Project.objects.count() < 2

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Project] = None) -> bool:
        if obj and obj.organization.name == Bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request, obj)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", request.user.id)
        initial.setdefault("organization", state.get_cookie("organization"))
        initial.setdefault("from_email", request.user.email)
        return initial
