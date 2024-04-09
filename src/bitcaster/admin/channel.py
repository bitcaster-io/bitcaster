import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Channel

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class ChannelAdmin(BaseAdmin, admin.ModelAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "application", "dispatcher_")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application", LinkedAutoCompleteFilter.factory(parent="organization")),
        "active",
    )

    def dispatcher_(self, obj: Channel) -> str:
        return obj.dispatcher.name

    def get_queryset(self, request: HttpRequest) -> QuerySet[Channel]:
        return super().get_queryset(request).select_related("application__project__organization")
