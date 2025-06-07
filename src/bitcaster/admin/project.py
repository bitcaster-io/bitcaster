import logging
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.decorators import button, view
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from bitcaster.models import Project

from ..constants import bitcaster
from ..forms.project import ProjectChangeForm
from ..utils.django import url_related
from .base import BaseAdmin, ButtonColor
from .mixins import LockMixinAdmin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class ProjectAdmin(BaseAdmin, LockMixinAdmin[Project], admin.ModelAdmin[Project]):
    search_fields = ("name",)
    list_display = ("name", "organization", "environments")
    list_filter = (
        ("organization", AutoCompleteFilter),
        # ("environments", ChoiceFilter),
    )
    autocomplete_fields = ("organization", "owner")
    exclude = ("locked",)
    form = ProjectChangeForm

    @view(login_required=True)
    def current(self, request: HttpRequest) -> HttpResponse:
        current: Project = Project.objects.local()[0]
        return HttpResponseRedirect(reverse("admin:bitcaster_project_change", args=[current.pk]))

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}

        extra_context["show_save"] = bool(object_id)
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = not object_id

        return super().changeform_view(request, object_id, form_url, extra_context)

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        visible=lambda s: s.context["original"].name != bitcaster.PROJECT,
    )
    def add_application(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Application

        return HttpResponseRedirect(url_related(Application, op="add", project=pk))

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        visible=lambda s: s.context["original"].name != bitcaster.PROJECT,
    )
    def add_distribution_list(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import DistributionList

        return HttpResponseRedirect(url_related(DistributionList, op="add", project=pk))

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        visible=lambda s: s.context["original"].name != bitcaster.PROJECT,
    )
    def add_channel(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Channel

        return HttpResponseRedirect(url_related(Channel, op="add", project=pk))

    def get_readonly_fields(self, request: HttpRequest, obj: Project | None = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.organization.name == bitcaster.ORGANIZATION:
            base.extend(["name", "slug", "organization", "subject_prefix"])
        return base

    def has_add_permission(self, request: HttpRequest, obj: Project | None = None) -> bool:
        return super().has_add_permission(request) and Project.objects.count() < 2

    def has_delete_permission(self, request: HttpRequest, obj: Project | None = None) -> bool:
        if obj and obj.organization.name == bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request) and super().has_delete_permission(request, obj)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("owner", request.user.id)
        initial.setdefault("from_email", request.user.email)
        return initial
