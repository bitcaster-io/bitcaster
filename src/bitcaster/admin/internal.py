import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.db.models import QuerySet
from django.http import HttpRequest

from ..models.internal import LogMessage
from .base import BaseAdmin, BitcasterModelAdmin

logger = logging.getLogger(__name__)


class LogMessageAdmin(BaseAdmin, BitcasterModelAdmin[LogMessage]):
    search_fields = ("name",)
    list_display = ("created", "level", "application")
    list_filter = (
        ("level", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
    )
    readonly_fields = ("application", "created", "level", "application")

    def get_queryset(self, request: HttpRequest) -> QuerySet[LogMessage]:
        return super().get_queryset(request).select_related("application")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: LogMessage | None = None) -> bool:
        return False
