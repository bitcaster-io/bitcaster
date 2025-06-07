import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django import forms
from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import ValidationError
from django.forms import Media
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from bitcaster.admin.base import BaseAdmin
from bitcaster.admin.filters import EnvironmentFilter
from bitcaster.auth.constants import Grant
from bitcaster.forms.mixins import Scoped3FormMixin
from bitcaster.models import ApiKey, Application, Event, Organization, Project  # noqa
from bitcaster.state import state
from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.contrib.admin.options import _ListOrTuple
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class ApiKeyForm(Scoped3FormMixin[ApiKey], forms.ModelForm[ApiKey]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.local(),
        required=True,
    )

    class Meta:
        model = ApiKey
        exclude = ("token",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            choices = [(k, k) for k in self.instance.project.environments]
            self.fields["environments"] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                required=False,
            )

    def clean(self) -> dict[str, Any]:
        super().clean()
        if self.instance.pk is None and (g := self.cleaned_data.get("grants")):
            a = self.cleaned_data.get("application")
            if Grant.EVENT_TRIGGER in g and not a:
                raise ValidationError(_("Application must be set if EVENT_TRIGGER is granted"))
        return self.cleaned_data


class ApiKeyAdmin(BaseAdmin, ModelAdmin["ApiKey"]):
    search_fields = ("name",)
    list_display = ("name", "user", "organization", "project", "application", "environments")
    list_filter = (
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="project")),
        EnvironmentFilter,
    )
    autocomplete_fields = ("user", "application", "organization", "project")
    form = ApiKeyForm
    save_as_continue = False

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[ApiKey]":
        return super().get_queryset(request).select_related("application")

    def get_readonly_fields(
        self, request: HttpRequest, obj: ApiKey | None = None
    ) -> list[str] | tuple[str, ...] | tuple[()]:
        if obj and obj.pk:
            return ["application", "organization", "project"]
        return self.readonly_fields

    def get_exclude(self, request: "HttpRequest", obj: "ApiKey | None" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk:
            return ["key"]
        return ["key", "environments"]

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        return {
            "user": request.user.id,
            "name": "Key-1",
            "organization": state.get_cookie("organization"),
            "project": state.get_cookie("project"),
            "application": state.get_cookie("application"),
        }

    def response_add(self, request: HttpRequest, obj: ApiKey, post_url_continue: str | None = None) -> HttpResponse:
        return HttpResponseRedirect(reverse("admin:bitcaster_apikey_show_key", args=[obj.pk]))

    @button()
    def show_key(self, request: HttpRequest, pk: str) -> HttpResponse:
        obj: ApiKey | None = self.get_object(request, pk)
        if is_root(request):
            expires = None
            expired = False
        else:
            expires = obj.created + timedelta(seconds=10)
            expired = timezone.now() > expires
        media = Media(js=["admin/js/vendor/jquery/jquery.js", "admin/js/jquery.init.js", "bitcaster/js/copy.js"])
        ctx = self.get_common_context(request, pk, media=media, expires=expires, expired=expired, title=_("Info"))
        return TemplateResponse(request, "admin/apikey/created.html", ctx)
