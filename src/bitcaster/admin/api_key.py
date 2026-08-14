from typing import TYPE_CHECKING, Any, cast

import logging
from datetime import timedelta

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from flags.state import flag_enabled

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.auth.constants import Grant
from bitcaster.forms.mixins import Scoped3FormMixin
from bitcaster.models import ApiKey, Application, Event, Organization, Project  # noqa
from bitcaster.models.key import ApiKeyKind
from bitcaster.state import state
from bitcaster.utils.security import is_root

from .base import BaseAdmin
from .filters import EnvironmentFilter
from ..utils.widgets import SmartMedia

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.admin.options import _ListOrTuple
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class ApiKeyForm(Scoped3FormMixin[ApiKey], forms.ModelForm[ApiKey]):
    class Meta:
        model = ApiKey
        fields = (
            "name",
            "organization",
            "user",
            "kind",
            "grants",
            "environments",
            "project",
            "application",
            "allowed_origins",
            "expires_at",
            "is_active",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.project and self.instance.project.environments:
            choices = [(k, k) for k in self.instance.project.environments]
            self.fields["environments"] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                required=False,
            )

    def clean(self) -> dict[str, Any]:
        cleaned_data = cast("dict[str, Any]", super().clean())
        if self.instance.pk is None and (g := cleaned_data.get("grants")):
            a = cleaned_data.get("application")
            if Grant.EVENT_TRIGGER in g and not a:
                raise ValidationError(_("Application must be set if EVENT_TRIGGER is granted"))
        kind = cleaned_data.get("kind", ApiKeyKind.SERVER)
        grants = cleaned_data.get("grants") or []
        if kind == ApiKeyKind.WEB:
            if not cleaned_data.get("application"):
                raise ValidationError(_("Web keys must be scoped to an application"))
            if set(grants) != {Grant.WEB_TRIGGER}:
                raise ValidationError(_("Web keys can only have the WEB_TRIGGER grant"))
            if not cleaned_data.get("allowed_origins"):
                raise ValidationError(_("Web keys require at least one allowed origin"))
        elif Grant.WEB_TRIGGER in grants:
            raise ValidationError(_("WEB_TRIGGER is only allowed for web keys"))
        return cleaned_data


class ApiKeyAdmin(BaseAdmin[ApiKey]):
    search_fields = ("name",)
    list_display = (
        "name",
        "kind",
        "user",
        "organization",
        "project",
        "application",
        "environments",
        "expires_at",
        "is_active",
    )
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="project")),
        EnvironmentFilter,
        "kind",
        "is_active",
    )
    autocomplete_fields = ("user", "application", "organization", "project")
    form = ApiKeyForm
    save_as_continue = False
    change_form_outer_before_template = "bitcaster/admin/apikey/outer_before.html"

    def get_queryset(self, request: HttpRequest) -> "QuerySet[ApiKey]":
        return super().get_queryset(request).select_related("application")

    def get_readonly_fields(self, request: HttpRequest, obj: ApiKey | None = None) -> list[str]:
        if obj and obj.pk:
            return ["organization", "project"]
        return list(self.readonly_fields)

    def get_exclude(self, request: HttpRequest, obj: ApiKey | None = None) -> "_ListOrTuple[str]":
        if flag_enabled("DEVELOP_FULL_EDIT"):
            return []
        if obj and obj.pk:
            return ["key"]
        return ["key", "environments"]

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "user": str(request.user.id),
            "name": "Key-1",
            "organization": state.get_cookie("organization"),
            "project": state.get_cookie("project"),
            "application": state.get_cookie("application"),
        }

    def response_add(self, request: HttpRequest, obj: ApiKey, post_url_continue: str | None = None) -> HttpResponse:
        return HttpResponseRedirect(reverse("admin:bitcaster_apikey_show_key", args=[obj.pk]))

    @button()  # type: ignore[arg-type]
    def show_key(self, request: HttpRequest, pk: str) -> HttpResponse:
        obj: ApiKey = self.get_object_or_404(request, pk)
        if is_root(request):
            expires = None
            expired = False
        else:
            expires = obj.created + timedelta(seconds=10)
            expired = timezone.now() > expires
        media = SmartMedia(
            js=[
                "admin/js/vendor/jquery/jquery{min}.js",
                "admin/js/jquery.init{min}.js",
                "bitcaster/js/copy{min}.js",
            ]
        )
        ctx = self.get_common_context(
            request, pk, bae=obj.get_bae(), media=media, expires=expires, expired=expired, action_title=_("Info")
        )
        return TemplateResponse(request, "bitcaster/admin/apikey/created.html", ctx)
