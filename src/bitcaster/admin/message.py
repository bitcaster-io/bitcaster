import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Message

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class MessageAdmin(BaseAdmin, admin.ModelAdmin[Message]):
    search_fields = ("name",)
    list_display = ("name", "channel", "event")
    list_filter = (
        ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
        ("event", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
    )
    autocomplete_fields = ("channel", "event")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Message]:
        return super().get_queryset(request).select_related()
