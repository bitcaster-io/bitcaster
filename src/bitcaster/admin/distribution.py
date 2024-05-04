import logging
from typing import TYPE_CHECKING, Optional

from adminfilters.autocomplete import LinkedAutoCompleteFilter
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
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
    autocomplete_fields = ("project",)
    filter_horizontal = ("recipients",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[DistributionList]:
        return super().get_queryset(request).select_related("project__organization")

    def get_readonly_fields(
        self, request: "HttpRequest", obj: "Optional[DistributionList]" = None
    ) -> "_ListOrTuple[str]":
        if obj and obj.name == DistributionList.ADMINS:
            return ["name", "project"]
        return []

    def has_delete_permission(self, request: HttpRequest, obj: Optional[DistributionList] = None) -> bool:
        if obj and obj.name == DistributionList.ADMINS:
            return False
        return super().has_delete_permission(request, obj)
