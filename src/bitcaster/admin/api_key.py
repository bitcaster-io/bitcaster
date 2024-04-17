import logging
from typing import TYPE_CHECKING, Optional

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.contrib.admin.options import _FieldGroups, _ListOrTuple

    from bitcaster.models import ApiKey  # noqa

logger = logging.getLogger(__name__)


class ApiKeyAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin["ApiKey"]):
    search_fields = ("name",)
    list_display = ("name", "user", "application")
    list_filter = (
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
    )
    autocomplete_fields = ("user", "application")

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[ApiKey]":
        return super().get_queryset(request).select_related("application")

    def get_fields(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_FieldGroups":
        ret: list = super().get_fields(request, obj)
        if not is_root(request) and "key" in ret:
            ret.remove("key")
        return ret

    def get_exclude(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        return ["key", "application"]

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["key", "application"]
        return super().get_readonly_fields(request, obj)