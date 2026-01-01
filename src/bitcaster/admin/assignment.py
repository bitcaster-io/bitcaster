import logging
from typing import TYPE_CHECKING, Any, TypeVar

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from bitcaster.admin.base import BaseAdmin, BitcasterModelAdmin, ButtonColor
from bitcaster.forms.assignment import AssignmentForm
from bitcaster.models import Address, Assignment

if TYPE_CHECKING:
    from django.forms import ModelForm

    AssignmentT = TypeVar("AssignmentT", bound=Assignment)
    AddressT = TypeVar("AddressT", bound=Address)

logger = logging.getLogger(__name__)


class AssignmentAdmin(BaseAdmin, BitcasterModelAdmin[Assignment]):
    search_fields = ("address__name",)
    list_display = ("address", "channel", "validated", "active")
    list_filter = (
        "channel",
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
