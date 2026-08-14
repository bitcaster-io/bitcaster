from typing import TYPE_CHECKING

from adminfilters.autocomplete import LinkedAutoCompleteFilter

from bitcaster.models import ClientToken

from .base import BaseAdmin
from .filters import EnvironmentFilter

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class ClientTokenAdmin(BaseAdmin[ClientToken]):
    search_fields = ("token",)
    list_display = ("short_token", "user", "application", "event", "environments", "expires_at", "is_active", "created")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="project")),
        EnvironmentFilter,
        "is_active",
    )
    autocomplete_fields = ("user", "parent", "event", "application", "organization", "project")
    readonly_fields = ("token", "user", "parent", "last_used_at", "created", "last_updated", "version")
    fields = (
        "token",
        "user",
        "parent",
        "organization",
        "project",
        "application",
        "event",
        "environments",
        "allowed_origins",
        "expires_at",
        "is_active",
        "last_used_at",
        "created",
        "last_updated",
        "version",
    )

    def short_token(self, obj: "ClientToken") -> str:
        return f"{obj.token[:8]}…"

    short_token.short_description = "Token"

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[ClientToken]":
        return super().get_queryset(request).select_related("application", "user", "event")

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return False
