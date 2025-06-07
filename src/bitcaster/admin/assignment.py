import logging
from typing import TYPE_CHECKING, Any, TypeVar

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _

from bitcaster.admin.base import BaseAdmin, ButtonColor
from bitcaster.forms.assignment import AssignmentForm
from bitcaster.forms.widgets import AutocompletSelectEnh
from bitcaster.models import Address, Assignment

if TYPE_CHECKING:
    from django.db.models import ForeignKey
    from django.db.models.fields.related import _ST
    from django.forms import ModelChoiceField, ModelForm

    from bitcaster.types.django import AnyModel

    # _ST = TypeVar("_ST")
    AssignmentT = TypeVar("AssignmentT", bound=Assignment)
    AddressT = TypeVar("AddressT", bound=Address)

logger = logging.getLogger(__name__)


class AssignmentAdmin(BaseAdmin, admin.ModelAdmin[Assignment]):
    search_fields = ("address__name",)
    list_display = ("address", "channel", "validated", "active")
    list_filter = (
        "channel",
        # ("channel__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("channel__project", AutoCompleteFilter),
        ("address__user", LinkedAutoCompleteFilter.factory(parent=None)),
        ("address", LinkedAutoCompleteFilter.factory(parent="address__user")),
    )
    autocomplete_fields = ("address", "channel")
    form = AssignmentForm
    readonly_fields = ["validated"]

    def get_form(
        self, request: HttpRequest, obj: Assignment | None = None, change: bool = False, **kwargs: Any
    ) -> "type[ModelForm[Assignment]]":
        return super().get_form(request, obj, change, **kwargs)

    def formfield_for_foreignkey(
        self, db_field: "ForeignKey[Assignment, _ST]", request: HttpRequest, **kwargs: Any
    ) -> "ModelChoiceField[AnyModel]":
        form_field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "address":
            filters = {}
            if user := request.GET.get("user", None):
                filters = {"user": user}
            form_field.widget = AutocompletSelectEnh(db_field, self.admin_site, filters=filters)
            form_field.queryset = form_field.queryset.filter(**filters)
        return form_field  # type: ignore[return-value]

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def validate(self, request: HttpRequest, pk: str) -> "HttpResponse":
        v: Assignment = self.get_object_or_404(request, pk)
        if v.channel.dispatcher.need_subscription:
            self.message_user(request, _("Cannot be validated."), messages.ERROR)
        else:
            v.validated = True
            v.save()
            self.message_user(request, _("Validated."))

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        ch_pk = request.GET.get("channel", None)
        addr_pk = request.GET.get("address", None)
        return {
            "address": addr_pk,
            "channel": ch_pk,
        }
