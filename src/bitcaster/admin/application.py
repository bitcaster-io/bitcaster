import logging
from typing import TYPE_CHECKING, Any, Optional

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest

from bitcaster.forms.application import ApplicationChangeForm
from bitcaster.models import Application

from ..state import state
from .base import BaseAdmin
from .mixins import LockMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


logger = logging.getLogger(__name__)


class ApplicationAdmin(BaseAdmin, LockMixin[Application], admin.ModelAdmin[Application]):
    search_fields = ("name",)
    list_display = ("name", "project", "organization", "active", "locked")
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
        "active",
        "locked",
    )
    autocomplete_fields = ("project", "owner")
    readonly_fields = ["locked"]
    form = ApplicationChangeForm

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project", "project__organization", "owner")

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

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "owner": request.user.id,
            "project": state.get_cookie("project"),
        }
