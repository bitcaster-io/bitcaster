import logging
from typing import TYPE_CHECKING, Any, TypeVar

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin
from django.db.models import ForeignKey
from django.forms import ModelChoiceField, ModelForm
from django.http import HttpRequest

from bitcaster.admin.base import BaseAdmin
from bitcaster.forms.validation import ValidationForm
from bitcaster.forms.widgets import AutocompletSelectEnh
from bitcaster.models import Address, Validation

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel

    ValidationT = TypeVar("ValidationT", bound=Validation)
    AddressT = TypeVar("AddressT", bound=Address)

logger = logging.getLogger(__name__)


class ValidationAdmin(BaseAdmin, admin.ModelAdmin[Validation]):
    search_fields = ("address__name",)
    list_display = ("address", "channel")
    list_filter = (
        "channel",
        ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel__application__project", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
        ("channel__application", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
    )
    autocomplete_fields = ("address", "channel")
    form = ValidationForm

    def get_form(
        self, request: HttpRequest, obj: Validation | None = None, change: bool = False, **kwargs: Any
    ) -> "type[ModelForm[Validation]]":
        frm = super().get_form(request, obj, change, **kwargs)
        return frm

    def formfield_for_foreignkey(
        self, db_field: "ForeignKey[Validation, AnyModel]", request: HttpRequest, **kwargs: Any
    ) -> "ModelChoiceField[AnyModel]":
        form_field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "address":
            filters = {}
            if user := request.GET.get("user", None):
                filters = {"user": user}
            form_field.widget = AutocompletSelectEnh(db_field, self.admin_site, filters=filters)
            form_field.queryset = form_field.queryset.filter(**filters)
        return form_field

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        ch_pk = request.GET.get("channel", None)
        addr_pk = request.GET.get("address", None)
        return {
            "address": addr_pk,
            "channel": ch_pk,
        }
