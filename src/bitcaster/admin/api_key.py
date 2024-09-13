import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from bitcaster.auth.constants import Grant
from bitcaster.forms.fields import Select2TagField
from bitcaster.forms.mixins import Scoped3FormMixin
from bitcaster.forms.widgets import AutocompletSelectEnh
from bitcaster.models import ApiKey, Application, Event, Organization, Project  # noqa
from bitcaster.state import state
from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.contrib.admin.options import _ListOrTuple

logger = logging.getLogger(__name__)


class ApiKeyForm(Scoped3FormMixin[ApiKey], forms.ModelForm[ApiKey]):
    environments = Select2TagField(required=False)
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        widget=AutocompletSelectEnh(ApiKey._meta.get_field("organization"), admin.site),
    )

    class Meta:
        model = ApiKey
        exclude = ("token",)

    def clean(self) -> dict[str, Any]:
        prj: Optional[Project]
        prj_envs: list[str] = []
        envs: list[str] = []
        super().clean()
        if self.instance.pk is None and (g := self.cleaned_data.get("grants")):
            a = self.cleaned_data.get("application")
            if Grant.EVENT_TRIGGER in g and not a:
                raise ValidationError(_("Application must be set if EVENT_TRIGGER is granted"))
        if self.instance.pk and self.instance.project:
            prj_envs = self.instance.project.environments or []
            envs = self.cleaned_data.get("environments", [])
        elif prj := self.cleaned_data.get("project"):
            prj_envs = prj.environments or []
            envs = self.cleaned_data.get("environments", [])
        if not set(envs).issubset(prj_envs):
            raise ValidationError({"environments": "One or more values are not available in the project"})

        return self.cleaned_data


class ApiKeyAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin, admin.ModelAdmin["ApiKey"]):
    search_fields = ("name",)
    list_display = ("name", "user", "organization", "project", "application", "environments")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="project")),
    )
    autocomplete_fields = ("user", "application", "organization", "project")
    form = ApiKeyForm

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[ApiKey]":
        return super().get_queryset(request).select_related("application")

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[ApiKey] = None
    ) -> list[str] | tuple[str, ...] | tuple[()]:
        if obj and obj.pk:
            return ["application", "organization", "project"]
        return self.readonly_fields

    # def get_fields(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_FieldGroups":
    #     ret = list(super().get_fields(request, obj))
    #     if not is_root(request) and "key" in ret:
    #         ret.remove("key")
    #     return ret

    def get_exclude(self, request: "HttpRequest", obj: "Optional[ApiKey]" = None) -> "_ListOrTuple[str]":
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
        return HttpResponseRedirect(reverse("admin:bitcaster_apikey_created", args=[obj.pk]))

    @view()
    def created(self, request: HttpRequest, pk: str) -> HttpResponse:
        obj: ApiKey = self.get_object(request, pk)  # type: ignore[assignment]
        expires = obj.created + timedelta(seconds=10)
        expired = timezone.now() > expires
        ctx = self.get_common_context(request, pk, expires=expires, expired=expired, title=_("Info"))
        return TemplateResponse(request, "admin/apikey/created.html", ctx)

    @button(visible=lambda s: is_root(s.context["request"]))
    def show_key(self, request: HttpRequest, pk: str) -> HttpResponse:  # noqa
        obj: ApiKey = self.get_object(request, pk)  # type: ignore[assignment]
        self.message_user(request, str(obj.key), messages.WARNING)
