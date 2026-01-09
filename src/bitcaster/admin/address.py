import logging
from typing import TYPE_CHECKING, Any, TypeVar

from admin_extra_buttons.decorators import view
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import messages
from django.contrib.admin import helpers
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from unfold.admin import TabularInline

from bitcaster.admin.base import BaseAdmin
from bitcaster.forms.address import AddressForm, AssignToChannelForm
from bitcaster.models import Address, Assignment

from .base import BitcasterModelAdmin

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.contrib.admin.options import InlineModelAdmin

    from bitcaster.types.django import AnyModel_co

    AddressT = TypeVar("AddressT", bound=Address)


class InlineValidation(TabularInline["Assignment", "AddressAdmin"]):
    model = Assignment
    extra = 0
    fields = ["channel", "validated", "active"]

    def has_change_permission(self, request, obj=None):
        return False


class AddressAdmin(BaseAdmin, BitcasterModelAdmin[Address]):
    search_fields = ("name", "value")
    list_display = ("user", "name", "value", "type")
    list_filter = (
        ("user", LinkedAutoCompleteFilter.factory(parent=None)),
        ("assignments__channel", AutoCompleteFilter),
        ("assignments__distributionlist__notifications__event", AutoCompleteFilter),
        "type",
    )
    autocomplete_fields = ("user",)
    form = AddressForm
    inlines = [InlineValidation]
    actions = ["assign_to_channel"]

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
    ) -> "list[type[InlineModelAdmin[Address, AnyModel_co]]]":
        if obj is None:
            return []
        return super().get_inlines(request, obj)

    @view()
    def assign_to_channel_single(self, request: HttpRequest, pk: str) -> "HttpResponse | None":
        obj: Address = self.get_object_or_404(request, pk)
        from bitcaster.models import Channel

        try:
            ch = Channel.objects.get(pk=request.GET.get("ch"))
            obj.assignments.get_or_create(channel=ch)
            self.message_user(request, _("Channel successfully assigned"))
        except Channel.DoesNotExist:
            self.message_user(request, _("Channel not found"), level=messages.ERROR)
        return HttpResponseRedirectToReferrer(request)

    def assign_to_channel(self, request: HttpRequest, queryset: QuerySet[Address]) -> "HttpResponse | None":
        ctx = self.get_common_context(request, action_title=_("Assign to Channel"))
        initial = {
            "_selected_action": request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
            "select_across": request.POST.get("select_across") == "1",
            "action": request.POST.get("action", ""),
        }
        if "apply" in request.POST:
            form = AssignToChannelForm(request.POST, request.FILES)
            if form.is_valid():
                ch = form.cleaned_data["channel"]
                assignments = [
                    Assignment(address=addr, channel=ch) for addr in queryset.exclude(assignments__channel=ch)
                ]
                created = Assignment.objects.bulk_create(assignments)
                self.message_user(request, _(f"Successfully assigned channel to {ch} {len(created)} addresses."))
                return HttpResponseRedirect(reverse(f"{self.admin_site.name}:bitcaster_address_changelist"))

        else:
            config_form = AssignToChannelForm(initial=initial)
            ctx["form"] = config_form

        return render(request, "bitcaster/admin/address/assign_to_channel.html", ctx)
