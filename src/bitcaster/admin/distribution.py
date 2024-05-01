import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import DistributionList

from .base import BaseAdmin
from .mixins import TwoStepCreateMixin

logger = logging.getLogger(__name__)


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
