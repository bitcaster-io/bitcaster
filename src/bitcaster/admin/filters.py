from typing import TYPE_CHECKING

from adminactions.utils import flatten
from django.contrib.admin.filters import SimpleListFilter
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from bitcaster.models.user_message import UserMessageQuerySet

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django.db.models.query import QuerySet

    from bitcaster.models import Channel, UserMessage


class ChannelTypeFilter(SimpleListFilter):
    parameter_name = "type"
    title = "Type"
    prefixes = (
        ("abstract", _("Abstract")),
        ("project", _("Project")),
    )

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Channel]") -> tuple[tuple[str, str], ...]:
        return self.prefixes

    def queryset(self, request: HttpRequest, queryset: "QuerySet[Channel]") -> "QuerySet[Channel]":
        if self.value() == "abstract":
            return queryset.filter(organization__isnull=False, project__isnull=True)
        if self.value() == "project":
            return queryset.filter(organization__isnull=False, project__isnull=False)
        return queryset.all()


class EnvironmentFilter(SimpleListFilter):
    parameter_name = "env"
    title = "Environment"
    prefixes = (
        ("abstract", _("Abstract")),
        ("project", _("Project")),
    )

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Channel]") -> tuple[tuple[str, str], ...]:
        values = list(model_admin.model.objects.values_list("environments", flat=True))
        return tuple((k, k) for k in flatten(values))

    def queryset(self, request: HttpRequest, queryset: "QuerySet[Channel]") -> "QuerySet[Channel]":
        if self.value():
            return queryset.filter(environments__icontains=self.value())
        return queryset.all()


class UserMessageExpiredFilter(SimpleListFilter):
    parameter_name = "expired"
    title = "Expired"
    prefixes = (
        ("0", _("Expired")),
        ("1", _("Not expired")),
    )

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[UserMessage]") -> tuple[tuple[str, str], ...]:
        return self.prefixes

    def queryset(self, request: HttpRequest, queryset: "UserMessageQuerySet") -> "QuerySet[UserMessage]":
        if self.value() == "0":
            return queryset.expired()
        if self.value() == "1":
            return queryset.active()
        return queryset
