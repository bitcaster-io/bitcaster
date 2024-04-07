import logging

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Channel

logger = logging.getLogger(__name__)


class ChannelAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "application", "dispatcher")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application", LinkedAutoCompleteFilter.factory(parent="organization")),
        "active",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Channel]:
        return super().get_queryset(request).select_related("application__project__organization")
