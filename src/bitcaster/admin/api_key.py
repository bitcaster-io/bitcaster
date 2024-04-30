import logging
from typing import TYPE_CHECKING, Optional

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from bitcaster.forms.mixins import ScopedFormMixin
from bitcaster.models import ApiKey  # noqa
from bitcaster.state import state
from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.contrib.admin.options import _FieldGroups, _ListOrTuple


logger = logging.getLogger(__name__)


class ApiKeyForm(ScopedFormMixin, forms.ModelForm):
    class Meta:
        model = ApiKey
        fields = "__all__"


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
        ret: list = super().get_fields(request, obj)
        if not is_root(request) and "key" in ret:
            ret.remove("key")
        return ret

    def get_exclude(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["key", "application"]

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["key", "application"]
        return super().get_readonly_fields(request, obj)

    def get_changeform_initial_data(self, request):
        return {
            "user": request.user.id,
            "name": "Key-1",
            "organization": state.get_cookie("organization"),
            "project": state.get_cookie("project"),
            "application": state.get_cookie("application"),
        }
