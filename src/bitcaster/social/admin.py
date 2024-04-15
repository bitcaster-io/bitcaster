from typing import Any

from admin_extra_buttons.buttons import Button
from admin_extra_buttons.decorators import link
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin
from django.db import models
from django.db.models.fields import Field
from django.forms.fields import Field as FormField
from django.http import HttpRequest
from django.urls import reverse
from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from bitcaster.models import SocialProvider


@admin.register(SocialProvider)
class SocialProfileAdmin(ExtraButtonsMixin, admin.ModelAdmin[SocialProvider]):
    list_display = (
        "provider",
        "enabled",
    )

    def formfield_for_dbfield(
        self,
        db_field: Field,
        request: HttpRequest,
        **kwargs: Any,
    ) -> FormField | None:  # type: ignore[type-arg]
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if isinstance(db_field, models.JSONField):
            formfield.widget = SvelteJSONEditorWidget(
                props={
                    "mode": "text",
                    "askToFormat": True,
                    "mainMenuBar": False,
                    "navigationBar": False,
                    "indentation": 2,
                    "tabSize": 2,
                    "flattenColumns": False,
                }
            )
        return formfield

    @link()
    def test(self, button: Button) -> None:
        if original := button.context.get("original"):
            button.label = f"Login with '{original.label}'"
            button.href = reverse("social:begin", args=[original.code])

    #
    # def get_readonly_fields(self, request: "HttpRequest", obj: SocialProvider | None = None) -> list[str]:
    #     if obj and obj.pk:
    #         return ["provider", "configuration"]
    #     return []
    #
    # def get_fields(self, request: "HttpRequest", obj: Optional[SocialProvider] = None) -> "_FieldGroups":
    #     if obj and obj.pk:
    #         return ["provider", "enabled"]
    #     return super().get_fields(request, obj)
