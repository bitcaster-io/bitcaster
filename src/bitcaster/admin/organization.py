import logging
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.decorators import button, view
from django import forms
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Channel, Group, Organization

from ..constants import bitcaster
from ..state import state
from ..utils.django import url_related
from .base import BaseAdmin, BitcasterModelAdmin, ButtonColor

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class ImportFromFileForm(forms.Form):
    help_text = _(
        """
File must be a .csv file, comma separated `,` with 3 columns

_Headers must be provided and named: last_name, first_name, email. Order can be customised_

Es:

```
last_name,first_name,email
Joe,Doe,j.doe@example.com
```
"""
    )
    file = forms.FileField(help_text=_(".CSV file"))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), help_text=_("Add imported users to this Group"))


class OrganizationAdmin(BaseAdmin, BitcasterModelAdmin[Organization]):
    search_fields = ("name",)
    list_display = ("name", "from_email", "subject_prefix")
    autocomplete_fields = ("owner",)

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

    @view(login_required=True)
    def current(self, request: HttpRequest) -> HttpResponse:
        if current := Organization.objects.local().first():
            return HttpResponseRedirect(reverse("admin:bitcaster_organization_change", args=[current.pk]))
        return HttpResponseRedirect(reverse("admin:bitcaster_organization_add"))

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def channels(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponseRedirect(url_related(Channel, organization__exact=pk))

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def project(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Project

        if prj := Project.objects.filter(organization_id=pk).first():
            url = reverse("admin:bitcaster_project_change", args=[prj.pk])
        else:
            url = url_related(Project, op="add", organization=pk)
        state.add_cookie("wizard_channel_wizard", {"step": "prj", "step_data": {"mode": "new"}})
        return HttpResponseRedirect(url)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return super().has_add_permission(request) and Organization.objects.count() < 2

    def has_delete_permission(self, request: HttpRequest, obj: Organization | None = None) -> bool:
        if obj and obj.name == bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request) and super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj: Organization | None = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name == bitcaster.ORGANIZATION:
            base.extend(["name", "slug", "subject_prefix"])
        return base

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "owner": request.user.id,
        }
