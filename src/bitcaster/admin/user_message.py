import logging
from typing import TYPE_CHECKING, Any

from django.contrib.admin.filters import ChoicesFieldListFilter
from django.utils.translation import gettext as _
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.decorators import display

from ..models import UserMessage
from .base import BaseAdmin, BitcasterModelAdmin
from .filters import UserMessageExpiredFilter

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class HorizontalChoicesFieldListFilter(ChoicesFieldListFilter):
    horizontal = True  # Enable horizontal layout


class UserMessageAdmin(BaseAdmin, BitcasterModelAdmin[UserMessage]):
    list_display = ("created", "level_badge", "event", "user", "subject")
    list_filter = (
        ("user", AutocompleteSelectFilter),
        ("event", AutocompleteSelectFilter),
        UserMessageExpiredFilter,
    )
    change_form_template = "bitcaster/admin/usermessage/change_form.html"

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[UserMessage]":
        return super().get_queryset(request).select_related("user", "event")

    def has_add_permission(self, request: "HttpRequest", *args: Any, **kwargs: Any) -> bool:
        return False

    def has_change_permission(self, request, obj=...):
        return False

    @display(
        description=_("Level"),
        ordering="level",
        label={
            "INFO": "info",
        },
    )
    def level_badge(self, obj):
        return logging._levelToName[int(obj.level)]
