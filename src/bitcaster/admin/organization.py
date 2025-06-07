import logging
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.decorators import button, view
from django import forms
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Channel, Group, Organization

from ..constants import bitcaster
from ..forms.message import OrgTemplateCreateForm
from ..state import state
from ..utils.django import url_related
from ..utils.importer import import_users_to_org
from .base import BaseAdmin, ButtonColor

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


class OrganizationAdmin(BaseAdmin, admin.ModelAdmin[Organization]):
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

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def create_channel(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Channel

        from .channel import ChannelType

        return HttpResponseRedirect(
            url_related(
                Channel,
                op="add",
                organization=pk,
                mode=ChannelType.MODE_TEMPLATE,
                _from=reverse("admin:bitcaster_organization_change", args=[pk]),
            )
        )

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def templates(self, request: HttpRequest, pk: str) -> HttpResponse:
        status_code = 200
        ctx = self.get_common_context(request, pk, title="Edit/Create Template")
        org = ctx["original"]
        if request.method == "POST":
            form = OrgTemplateCreateForm(request.POST, organization=org)
            if form.is_valid():
                msg = org.message_set.create(name=form.cleaned_data["name"], channel=form.cleaned_data["channel"])
                ctx["message_created"] = msg
            else:
                status_code = 400
        else:
            form = OrgTemplateCreateForm(organization=org)
        ctx["message_templates"] = org.message_set.filter(project=None)
        ctx["form"] = form
        return TemplateResponse(request, "admin/message/create_message_template.html", ctx, status=status_code)

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

    @button(label="Import Users")
    def import_from_file(self, request: HttpRequest, pk: str) -> HttpResponse:
        ctx = self.get_common_context(request, pk)
        org: Organization = ctx["original"]
        if request.method == "POST":
            form = ImportFromFileForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    import_users_to_org(form.cleaned_data["file"], org, form.cleaned_data["group"], {})
                    return HttpResponseRedirect(reverse("admin:bitcaster_distributionlist_change", args=[org.pk]))
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)

        else:
            form = ImportFromFileForm()
        ctx["form"] = form
        return TemplateResponse(request, "admin/bitcaster/organization/import.html", ctx)
