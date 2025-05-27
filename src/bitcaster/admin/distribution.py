import logging
from typing import TYPE_CHECKING, Any

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import DistributionList

from .base import BaseAdmin
from .mixins import TwoStepCreateMixin

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


class DistributionListAdmin(BaseAdmin, TwoStepCreateMixin[DistributionList], admin.ModelAdmin[DistributionList]):
    search_fields = ("name",)
    list_display = ("name", "project")
    list_filter = (
        # ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        # ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
        ("project", LinkedAutoCompleteFilter.factory(parent=None)),
        ("recipients__address__user", AutoCompleteFilter.factory()),
    )
    autocomplete_fields = ("project",)
    filter_horizontal = ("recipients",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[DistributionList]:
        return super().get_queryset(request).select_related("project__organization")

    def get_readonly_fields(self, request: "HttpRequest", obj: "DistributionList | None" = None) -> "_ListOrTuple[str]":
        if obj and obj.name == DistributionList.ADMINS:
            return ["name", "project"]
        return []

    def has_delete_permission(self, request: HttpRequest, obj: DistributionList | None = None) -> bool:
        if obj and obj.name == DistributionList.ADMINS:
            return False
        return super().has_delete_permission(request, obj)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        from bitcaster.models import Project

        initial["project"] = Project.objects.local().first()
        return initial
