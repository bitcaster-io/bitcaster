import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse

from bitcaster.models import Channel, Organization, Project

from ..constants import Bitcaster
from ..forms.message import OrgTemplateCreateForm
from ..utils.django import url_related
from .base import BaseAdmin, ButtonColor

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


logger = logging.getLogger(__name__)


class OrganisationAdmin(BaseAdmin, admin.ModelAdmin[Organization]):
    search_fields = ("name",)
    list_display = ("name", "from_email", "subject_prefix")

    @button(html_attrs={"style": f"background-color:{ButtonColor.LINK}"})
    def projects(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponseRedirect(url_related(Project, organization__exact=pk))

    @button(html_attrs={"style": f"background-color:{ButtonColor.LINK}"})
    def channels(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponseRedirect(url_related(Channel, organization__exact=pk))

    @button(html_attrs={"style": f"background-color:{ButtonColor.ACTION}"})
    def templates(self, request: HttpRequest, pk: str) -> HttpResponse:
        status_code = 200
        ctx = self.get_common_context(request, pk)
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
        return Organization.objects.count() < 2

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Organization] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name.lower() == Bitcaster.ORGANIZATION:
            base.extend(["name", "slug"])
        return base

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "owner": request.user.id,
        }
