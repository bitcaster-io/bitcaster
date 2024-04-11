import logging
from typing import TYPE_CHECKING, TypeVar

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.models import Address, Validation

if TYPE_CHECKING:
    ValidationT = TypeVar("ValidationT", bound=Validation)
    AddressT = TypeVar("AddressT", bound=Address)

logger = logging.getLogger(__name__)


class InlineValidation(admin.TabularInline["Validation", "AddressAdmin"]):
    model = Validation
    extra = 0


class AddressAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin[Address]):
    search_fields = ("name",)
    list_display = ("user", "name", "value")
    list_filter = (
        ("user__roles__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("user", LinkedAutoCompleteFilter.factory(parent=None)),
    )
    autocomplete_fields = ("user",)

    inlines = [InlineValidation]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Address]:
        return super().get_queryset(request).select_related("user")


class ValidationAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin[Validation]):
    list_display = ("address", "channel")
    list_filter = (
        "channel",
        ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel__application__project", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
        ("channel__application", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
    )
    autocomplete_fields = ("address", "channel")
