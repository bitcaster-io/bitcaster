import logging
from typing import TYPE_CHECKING, TypeVar

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Address

from .validation import InlineValidation

if TYPE_CHECKING:
    AddressT = TypeVar("AddressT", bound=Address)

logger = logging.getLogger(__name__)


class AddressAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin[Address]):
    search_fields = ("name",)
    list_display = ("user", "name", "value", "type")
    list_filter = (
        ("user__roles__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("user", LinkedAutoCompleteFilter.factory(parent=None)),
        "type",
    )
    autocomplete_fields = ("user",)

    inlines = [InlineValidation]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Address]:
        return super().get_queryset(request).select_related("user")
