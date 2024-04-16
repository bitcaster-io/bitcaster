import logging
from typing import TYPE_CHECKING, TypeVar

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin

from bitcaster.models import Address, Validation

if TYPE_CHECKING:
    ValidationT = TypeVar("ValidationT", bound=Validation)
    AddressT = TypeVar("AddressT", bound=Address)

logger = logging.getLogger(__name__)


class ValidationAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin[Validation]):
    search_fields = ("address__name",)
    list_display = ("address", "channel")
    list_filter = (
        "channel",
        ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel__application__project", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
        ("channel__application", LinkedAutoCompleteFilter.factory(parent="channel__organization")),
    )
    autocomplete_fields = ("address", "channel")
