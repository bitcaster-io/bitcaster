import logging

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from bitcaster.models import Application, Organization, Project

from .base import BaseAdmin

logger = logging.getLogger(__name__)


class OrganisationAdmin(BaseAdmin, admin.ModelAdmin[Organization]):
    search_fields = ("name",)
    list_display = ("name",)

    @button()
    def projects(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponse("Projects")


class ProjectAdmin(BaseAdmin, admin.ModelAdmin[Project]):
    search_fields = ("name",)
    list_display = ("name",)
    list_filter = (("organization", AutoCompleteFilter),)


class ApplicationAdmin(BaseAdmin, admin.ModelAdmin[Application]):
    search_fields = ("name",)
    list_display = ("name",)
    list_filter = (
        ("project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="project__organization")),
    )
