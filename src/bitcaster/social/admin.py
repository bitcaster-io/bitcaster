from typing import Any

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


@admin.register(SocialProvider)
class SocialProviderAdmin(ExtraButtonsMixin, BitcasterModelAdmin[SocialProvider]):
    list_display = ("label", "slug", "provider", "enabled", "client_id")
    change_form_template = "admin/social/socialprovider/change_form.html"
    form = SocialProviderForm
    fieldsets = (
        (_("General"), {"classes": ["tab"], "fields": ["label", "slug", "enabled"]}),
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
