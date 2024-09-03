import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from bitcaster.models import Channel, Organization

from ..constants import Bitcaster
from ..forms.message import OrgTemplateCreateForm
from ..state import state
from ..utils.django import url_related
from .base import BaseAdmin, ButtonColor

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

logger = logging.getLogger(__name__)


class OrganisationAdmin(BaseAdmin, admin.ModelAdmin[Organization]):
    search_fields = ("name",)
    list_display = ("name", "from_email", "subject_prefix")
    autocomplete_fields = ("owner",)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Optional[str] = None,
        form_url: str = "",
        extra_context: Optional[dict[str, Any]] = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}

        extra_context["show_save"] = bool(object_id)
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = not object_id

        return super().changeform_view(request, object_id, form_url, extra_context)

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def channels(self, request: HttpRequest, pk: str) -> HttpResponse:
        return HttpResponseRedirect(url_related(Channel, organization__exact=pk))

    @button(html_attrs={"class": ButtonColor.LINK.value})
    def create_project(self, request: HttpRequest, pk: str) -> HttpResponse:
        from bitcaster.models import Project

        # "{\"step\":\"org\"\054\"step_data\":{\"mode\":{\"csrfmiddlewaretoken\":[\"0UafnqMrhvEt6PLBEywxatmYvsOKGpVtOYe1fu17rY5wH2Wyi3wkNoeM15wOCstZ\"]\054\"channel_wizard-current_step\":[\"mode\"]\054\"mode-operation\":[\"new\"]}}\054\"step_files\":{\"mode\":{}}\054\"extra_data\":{}}:1shv4A:w6bsHlrfLKgjTqN7vSUjRKVPen0uAq9dY9BjloqXyRY"
        state.add_cookie("wizard_channel_wizard", {"step": "prj", "step_data": {"mode": "new"}})
        return HttpResponseRedirect(url_related(Project, op="add", organization=pk))

    @button(html_attrs={"class": ButtonColor.LINK.value})
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

    @button(html_attrs={"class": ButtonColor.ACTION.value})
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
        return Organization.objects.count() < 2

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Organization] = None) -> bool:
        if obj and obj.name == Bitcaster.ORGANIZATION:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Organization] = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name == Bitcaster.ORGANIZATION:
            base.extend(["name", "slug", "subject_prefix"])
        return base

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "owner": request.user.id,
        }
