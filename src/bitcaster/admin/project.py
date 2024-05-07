import logging
from typing import TYPE_CHECKING, Any, Optional

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest

from bitcaster.models import Project

from ..constants import Bitcaster
from ..forms.project import ProjectChangeForm
from ..state import state
from .base import BaseAdmin
from .mixins import LockMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


logger = logging.getLogger(__name__)


class ProjectAdmin(BaseAdmin, LockMixin[Project], admin.ModelAdmin[Project]):
    search_fields = ("name",)
    list_display = ("name", "organization", "environments")
    list_filter = (
        ("organization", AutoCompleteFilter),
        # ("environments", ChoiceFilter),
    )
    autocomplete_fields = ("organization",)
    exclude = ("locked",)
    form = ProjectChangeForm

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Project] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.organization.name == Bitcaster.ORGANIZATION:
            base.extend(["name", "slug", "organization"])
        return base

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Project] = None) -> bool:
        if obj and obj.organization.name == Bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request, obj)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "owner": request.user.id,
            "organization": state.get_cookie("organization"),
        }
