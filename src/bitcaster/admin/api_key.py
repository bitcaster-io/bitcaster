import logging
from typing import TYPE_CHECKING, Optional

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

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

    def get_exclude(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        return ["key", "application"]
        return super().get_exclude(request, obj)

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["key", "application"]
        return super().get_readonly_fields(request, obj)
