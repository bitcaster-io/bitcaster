import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django_select2 import forms as s2forms

from bitcaster.forms.mixins import ScopedFormMixin
from bitcaster.models import ApiKey, Application, Organization, Project  # noqa
from bitcaster.state import state
from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.contrib.admin.options import _FieldGroups, _ListOrTuple


logger = logging.getLogger(__name__)


class OrganizationWidget(s2forms.ModelSelect2Widget):
    search_fields = ["name__istartswith"]


class ProjectWidget(s2forms.ModelSelect2Widget):
    search_fields = ["name__istartswith"]
    dependent_fields = ({"organization": "organization"},)


class ApiKeyForm(ScopedFormMixin[ApiKey], forms.ModelForm[ApiKey]):

    class Meta:
        model = ApiKey
        fields = "__all__"
        # widgets = {
        #     "organization": OrganizationWidget,
        #     "": ProjectWidget,
        # }


# class ApiKeyForm1(ScopedFormMixin[ApiKey], forms.ModelForm[ApiKey]):
#     class Meta:
#         model = ApiKey
#         fields = ("organization",)
#
#
# class ApiKeyForm2(ScopedFormMixin[ApiKey], forms.ModelForm[ApiKey]):
#     class Meta:
#         model = ApiKey
#         fields = ("project",)
#
#
# class ApiKeyForm3(ScopedFormMixin[ApiKey], forms.ModelForm[ApiKey]):
#     class Meta:
#         model = ApiKey
#         fields = ("application",)


class ApiKeyAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin["ApiKey"]):
    search_fields = ("name",)
    list_display = ("name", "user", "application")
    list_filter = (
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
    )
    autocomplete_fields = ("user", "application", "organization", "project")
    form = ApiKeyForm

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[ApiKey]":
        return super().get_queryset(request).select_related("application")

    def get_fields(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_FieldGroups":
        ret = list(super().get_fields(request, obj))
        if not is_root(request) and "key" in ret:
            ret.remove("key")
        return ret

    def get_exclude(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["key"]

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "user": request.user.id,
            "name": "Key-1",
            "organization": state.get_cookie("organization"),
            "project": state.get_cookie("project"),
            "application": state.get_cookie("application"),
        }

    def response_add(self, request: HttpRequest, obj: ApiKey, post_url_continue: str | None = None) -> HttpResponse:
        self.message_user(request, obj.key, messages.WARNING)
        return super().response_add(request, obj, post_url_continue)

    def add_view(
        self, request: HttpRequest, form_url: str = "", extra_context: Optional[dict[str, Any]] = None
    ) -> HttpResponse:
        ret = super().add_view(request, form_url, extra_context)
        return ret

    @button(visible=lambda s: is_root(s.context["request"]))
    def show_key(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj = self.get_object(request, pk)
        self.message_user(request, str(obj.key), messages.WARNING)
