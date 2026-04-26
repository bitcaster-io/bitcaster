import logging
from typing import TYPE_CHECKING, Any, TypeVar, cast

from admin_extra_buttons.decorators import view
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import messages
from django.contrib.admin import helpers
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from unfold.admin import TabularInline

from bitcaster.admin.base import BaseAdmin
from bitcaster.forms.address import AddressForm, AssignToChannelForm
from bitcaster.models import Address, Assignment, DistributionList, Notification

from .filters import AddressByList, AddressByNotification

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.admin.options import InlineModelAdmin

    AddressT = TypeVar("AddressT", bound=Address)


class InlineValidation(TabularInline[Assignment, Address]):
    model = Assignment
    extra = 0
    fields = ["channel", "validated", "active"]

    def has_change_permission(self, request: HttpRequest, obj: Assignment | None = None) -> bool:
        return False


class AddressAdmin(BaseAdmin[Address]):
    search_fields = ("name", "value")
    list_display = ("user", "name", "value", "type")
    list_filter = (
        ("user", LinkedAutoCompleteFilter.factory(parent=None)),
        ("assignments__channel", AutoCompleteFilter),
        AddressByList,
        AddressByNotification,
        "type",
    )
    autocomplete_fields = ("user",)
    form = AddressForm
    inlines = [InlineValidation]
    actions = ["assign_to_channel"]

    def get_readonly_fields(self, request: HttpRequest, obj: Address | None = None) -> list[str]:
        if obj is None:
            return list(super().get_readonly_fields(request, obj))
        return ["user", "type"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Address]:
        return super().get_queryset(request).select_related("user")

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        extra_context = extra_context or {}
        active_filters = []
        if dl_id := request.GET.get("dl"):
            try:
                dl = DistributionList.objects.get(pk=dl_id)
                active_filters.append(_("Distribution list: %s") % dl.name)
            except (DistributionList.DoesNotExist, ValueError):
                pass
        if not_id := request.GET.get("n"):
            try:
                notification = Notification.objects.get(pk=not_id)
                active_filters.append(_("Notification:  %s") % notification.name)
            except (Notification.DoesNotExist, ValueError):
                pass

        extra_context["active_filters"] = active_filters
        return super().changelist_view(request, extra_context=extra_context)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        user_pk = request.GET.get("user", str(request.user.pk))
        return {
            "user": user_pk,
            "name": "Address-1",
        }

    def get_inlines(self, request: HttpRequest, obj: Address | None = None) -> "list[type[InlineModelAdmin[Any, Any]]]":
        if obj is None:
            return []
        return cast("list[type[InlineModelAdmin[Any, Any]]]", super().get_inlines(request, obj))

    @view()  # type: ignore[arg-type]
    def assign_to_channel_single(self, request: HttpRequest, pk: str) -> HttpResponse:
        obj: Address = self.get_object_or_404(request, pk)
        from bitcaster.models import Channel

        try:
            ch = Channel.objects.get(pk=request.GET.get("ch"))
            obj.assignments.get_or_create(channel=ch)
            self.message_user(request, str(_("Channel successfully assigned")))
        except Channel.DoesNotExist:
            self.message_user(request, str(_("Channel not found")), level=messages.ERROR)
        return cast("HttpResponse", HttpResponseRedirectToReferrer(request))

    def assign_to_channel(self, request: HttpRequest, queryset: QuerySet[Address]) -> HttpResponse:
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
