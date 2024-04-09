import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from ..models.log import LogEntry
from .base import BaseAdmin

logger = logging.getLogger(__name__)


class LogEntryAdmin(BaseAdmin, admin.ModelAdmin[LogEntry]):
    search_fields = ("name",)
    list_display = ("created", "level", "application")
    list_filter = (
        ("level", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[LogEntry]:
        return super().get_queryset(request).select_related("application")
