import logging
from typing import TYPE_CHECKING, Any, TypeVar

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.admin.base import BaseAdmin
from bitcaster.forms.address import AddressForm
from bitcaster.models import Address, Assignment

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.contrib.admin.options import InlineModelAdmin

    from bitcaster.types.django import AnyModel

    AddressT = TypeVar("AddressT", bound=Address)


class InlineValidation(admin.TabularInline["Assignment", "AddressAdmin"]):
    model = Assignment
    extra = 0
    fields = ["channel", "validated", "active"]


class AddressAdmin(BaseAdmin, admin.ModelAdmin[Address]):
    search_fields = ("name", "value")
    list_display = ("user", "name", "value", "type")
    list_filter = (
        # ("user__roles__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("user", LinkedAutoCompleteFilter.factory(parent=None)),
        ("assignments__channel", AutoCompleteFilter),
        ("assignments__distributionlist__notifications__event", AutoCompleteFilter),
        "type",
    )
    autocomplete_fields = ("user",)
    form = AddressForm
    inlines = [InlineValidation]

    def get_readonly_fields(self, request: HttpRequest, obj: Address | None = None) -> tuple[str, ...] | list[str]:
        if obj is None:
            return super().get_readonly_fields(request, obj)
        return "user", "type"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Address]:
        return super().get_queryset(request).select_related("user")

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        user_pk = request.GET.get("user", request.user.pk)
        return {
            "user": user_pk,
            "name": "Address-1",
        }

    def get_inlines(
        self, request: HttpRequest, obj: Address | None = None
    ) -> "list[type[InlineModelAdmin[Address, AnyModel]]]":
        if obj is None:
            return []
        return super().get_inlines(request, obj)
