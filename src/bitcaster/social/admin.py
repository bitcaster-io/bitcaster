from typing import TYPE_CHECKING, Any

from admin_extra_buttons.mixins import ExtraButtonsMixin
from jsoneditor.forms import JSONEditor

from django.contrib import admin
from django.db import models
from django.db.models.fields import Field
from django.forms.fields import Field as FormField
from django.http import HttpRequest
from django.utils.translation import gettext as _

from bitcaster.admin.base import BitcasterModelAdmin
from bitcaster.models import SocialProvider
from bitcaster.social.forms import SocialProviderForm
from bitcaster.social.utils import is_own_login_provider

if TYPE_CHECKING:
    from django import forms


@admin.register(SocialProvider)
class SocialProviderAdmin(ExtraButtonsMixin, BitcasterModelAdmin[SocialProvider]):
    list_display = ("label", "provider", "enabled", "client_id")
    change_form_template = "admin/social/socialprovider/change_form.html"
    form = SocialProviderForm
    fieldsets = (
        (_("General"), {"classes": ["tab"], "fields": ["label", "enabled"]}),
        (
            _("Configuration"),
            {"classes": ["tab"], "fields": ["provider", "client_id", "secret", "key", "configuration"]},
        ),
    )

    def formfield_for_dbfield(self, db_field: Field[Any, Any], request: HttpRequest, **kwargs: Any) -> FormField | None:
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if isinstance(db_field, models.JSONField):
            formfield.widget = JSONEditor()
        return formfield

    def has_add_permission(self, request: HttpRequest) -> bool:
        if SocialProvider.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request: HttpRequest, obj: SocialProvider | None = None) -> bool:
        if obj is not None and is_own_login_provider(request, obj):
            return False
        return super().has_delete_permission(request, obj)

    def get_form(
        self, request: HttpRequest, obj: SocialProvider | None = None, change: bool = False, **kwargs: Any
    ) -> "type[forms.ModelForm[SocialProvider]]":
        form_class = super().get_form(request, obj, change=change, **kwargs)
        form_class.request = request
        return form_class
