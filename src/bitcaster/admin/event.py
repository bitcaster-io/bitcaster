import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Event

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class EventTypAdmin(BaseAdmin, admin.ModelAdmin[Event]):
    search_fields = ("name",)
    list_display = ("name", "application", "active")
    list_filter = (
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
        "active",
    )
    autocomplete_fields = ("application",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return super().get_queryset(request).select_related("application__project__organization")
