from typing import Any

import logging

from adminfilters.autocomplete import LinkedAutoCompleteFilter

from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Subscription
from bitcaster.utils.django import admin_toggle_bool_action

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class SubscriptionAdmin(BaseAdmin[Subscription]):
    search_fields = (
        "assignment__address__value",
        "notification__name",
    )
    list_display = ("user", "notification", "assignment", "active")
    list_filter = (
        "active",
        ("assignment__address__user", LinkedAutoCompleteFilter.factory(parent=None)),
        ("notification", LinkedAutoCompleteFilter.factory(parent=None)),
    )
    autocomplete_fields = ("notification", "assignment")
    actions = ["toggle_active"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Subscription]:
        return (
            super()
            .get_queryset(request)
            .select_related("notification", "assignment", "assignment__address", "assignment__address__user")
        )

    def toggle_active(self, request: HttpRequest, queryset: QuerySet[Subscription]) -> None:
        admin_toggle_bool_action(request, queryset, "active")

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        notification_pk = request.GET.get("notification", None)
        return {
            "notification": notification_pk,
        }
