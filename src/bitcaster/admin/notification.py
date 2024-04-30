import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Notification

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class NotificationAdmin(BaseAdmin, admin.ModelAdmin[Notification]):
    search_fields = ("name",)
    list_display = ("name",)
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
    autocomplete_fields = ("event", "distribution")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Notification]:
        return super().get_queryset(request).select_related("event", "distribution")
