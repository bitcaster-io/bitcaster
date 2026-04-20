from typing import TYPE_CHECKING, Any, cast

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import link
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin
from django.db import models
from django.db.models import Model
from django.db.models.fields import Field
from django.forms.fields import Field as FormField
from django.http import HttpRequest
from django.urls import reverse
from jsoneditor.forms import JSONEditor
from unfold.typing import FieldsetsType

from bitcaster.admin.base import BitcasterModelAdmin
from bitcaster.models import SocialProvider
from bitcaster.social.forms import SocialProviderAddForm, SocialProviderUpdateForm
from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from bitcaster.social.forms import SocialProviderForm


@admin.register(SocialProvider)
class SocialProviderAdmin(ExtraButtonsMixin, BitcasterModelAdmin[SocialProvider]):
    list_display = (
        "provider",
        "enabled",
    )
    change_form_template = "admin/social/socialprovider/change_form.html"

    def get_form(
        self, request: HttpRequest, obj: SocialProvider | None = None, change: bool = False, **kwargs: Any
    ) -> "type[SocialProviderForm]":
        if obj and obj.pk:
            self.form = SocialProviderUpdateForm
        else:
            self.form = SocialProviderAddForm
        return cast("SocialProviderUpdateForm", super().get_form(request, obj, change, **kwargs))

    def get_fieldsets(self, request: HttpRequest, obj: Model | None = None) -> FieldsetsType:
        return super().get_fieldsets(request, obj)

    def formfield_for_dbfield(self, db_field: Field[Any, Any], request: HttpRequest, **kwargs: Any) -> FormField | None:
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if isinstance(db_field, models.JSONField):
            formfield.widget = JSONEditor()
        return formfield

    @link()
    def login_with(self, button: ButtonWidget) -> None:
        if original := button.context.get("original"):
            button.label = f"Login with '{original.label}'"
            button.href = reverse("social:begin", args=[original.code])

    def get_readonly_fields(self, request: "HttpRequest", obj: SocialProvider | None = None) -> list[str]:
        if is_root(request):
            return []
        if obj and obj.pk:
            return ["provider", "configuration"]
        return []
