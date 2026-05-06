from typing import TYPE_CHECKING, Any

import logging

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import bitcaster
from bitcaster.models import DistributionList

from .base import BaseAdmin, ButtonColor
from .mixins import TwoStepCreateMixin

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from django.utils.datastructures import _ListOrTuple


class DistributionListAdmin(TwoStepCreateMixin[DistributionList], BaseAdmin[DistributionList]):
    search_fields = ("name",)
    list_display = ("name", "project")
    list_filter = (
        ("project", LinkedAutoCompleteFilter.factory(parent=None)),
        ("recipients__address__user", AutoCompleteFilter.factory()),
    )
    autocomplete_fields = ("project",)
    filter_horizontal = ("recipients",)
    fields = (
        "name",
        "project",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[DistributionList]:
        return super().get_queryset(request).select_related("project__organization")

    @button(label=_("Recipients"), html_attrs={"class": ButtonColor.LINK.value})  # type: ignore[arg-type]
    def members(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:bitcaster_member_changelist")
        return HttpResponseRedirect(f"{url}?dl={pk}")

    def get_readonly_fields(self, request: HttpRequest, obj: DistributionList | None = None) -> "_ListOrTuple[str]":
        if obj and obj.name == DistributionList.ADMINS:
            return ["name", "project"]
        return []

    def has_delete_permission(self, request: HttpRequest, obj: DistributionList | None = None) -> bool:
        if obj and obj.name == DistributionList.ADMINS and obj.project.organization.name == bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request, obj)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        from bitcaster.models import Project

        initial["project"] = Project.objects.local().first()
        return initial
