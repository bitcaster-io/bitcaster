import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Subscription, User

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class SubscriptionAdmin(BaseAdmin, admin.ModelAdmin[Subscription]):
    search_fields = ("name",)
    list_display = ("address", "user", "event", "active")
    list_filter = (
        ("event__application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        (
            "event__application__project",
            LinkedAutoCompleteFilter.factory(parent="event__application__project__organization"),
        ),
        ("event__application", LinkedAutoCompleteFilter.factory(parent="event__application__project")),
        ("event", LinkedAutoCompleteFilter.factory(parent="event__application")),
        # ("address_user", LinkedAutoCompleteFilter.factory(parent=None)),
        "active",
    )
    autocomplete_fields = ("event", "address")
    filter_horizontal = ("channels",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Subscription]:
        return (
            super()
            .get_queryset(request)
            .select_related("address", "address__user", "event__application__project__organization")
        )

    def user(self, obj: Subscription) -> "User":
        return obj.address.user
