import logging

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import (AutoCompleteFilter,
                                       LinkedAutoCompleteFilter)
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from bitcaster.models import Application, Organization, Project

logger = logging.getLogger(__name__)


class OrganisationAdmin(
    AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin[Organization]
):
    search_fields = ("name",)
    list_display = ("name",)

    @button()
    def projects(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponse("Projects")


class ProjectAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, admin.ModelAdmin[Project]):
    search_fields = ("name",)
    list_display = ("name",)
    list_filter = (("organization", AutoCompleteFilter),)


class ApplicationAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, admin.ModelAdmin[Application]):
    list_display = ("name",)
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
