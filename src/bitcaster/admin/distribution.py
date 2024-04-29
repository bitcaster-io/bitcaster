import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Subscription

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class DistributionListAdmin(BaseAdmin, admin.ModelAdmin[Subscription]):
    search_fields = ("name",)
    list_display = ("name",)
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
    autocomplete_fields = ("project",)
    filter_horizontal = ("recipients",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Subscription]:
        return super().get_queryset(request).select_related("project__organization")
