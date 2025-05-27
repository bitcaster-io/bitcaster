from typing import TYPE_CHECKING, Any

from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.http import HttpRequest

from bitcaster.auth.constants import DEFAULT_GROUP_NAME

if TYPE_CHECKING:
    from django.contrib.auth.models import Group
    from django.utils.datastructures import _ListOrTuple


class GroupAdmin(BaseGroupAdmin):
    def get_readonly_fields(self, request: "HttpRequest", obj: "Group | None" = None) -> "_ListOrTuple[str]":
        base = list(super().get_readonly_fields(request, obj))
        if obj and obj.name == DEFAULT_GROUP_NAME:
            base.append("name")
        return base

    def save_model(self, request: HttpRequest, obj: "Group", form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)
