import logging
from typing import TYPE_CHECKING

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from ..models import UserRole
from .base import BaseAdmin

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class UserRoleAdmin(BaseAdmin, admin.ModelAdmin[UserRole]):
    list_display = (
        "user",
        "organization",
        "group",
    )
    list_filter = (
        ("user", AutoCompleteFilter),
        # ("organization", AutoCompleteFilter),
        ("group", AutoCompleteFilter),
    )
    search_fields = ("user__username",)
    ordering = ("user__username",)
    autocomplete_fields = ("user", "organization", "group")

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[UserRole]":
        return super().get_queryset(request).select_related("user", "organization", "group")
