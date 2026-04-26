from typing import TYPE_CHECKING

from adminactions.utils import flatten
from django.contrib.admin.filters import SimpleListFilter
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.admin import ModelAdmin
    from django.db.models.query import QuerySet
    from django.utils.functional import _StrPromise

    from bitcaster.models import Address, Channel, User, UserMessage
    from bitcaster.models.user_message import UserMessageQuerySet


class ChannelTypeFilter(SimpleListFilter):
    parameter_name = "type"
    title = "Type"
    prefixes = (
        ("abstract", _("Abstract")),
        ("project", _("Project")),
    )

    def lookups(
        self, request: HttpRequest, model_admin: "ModelAdmin[Channel]"
    ) -> tuple[tuple[str, "str|_StrPromise"], ...]:
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

    def lookups(
        self, request: HttpRequest, model_admin: "ModelAdmin[UserMessage]"
    ) -> "tuple[tuple[str, str|_StrPromise], ...]":
        return self.prefixes

    def queryset(self, request: HttpRequest, queryset: "UserMessageQuerySet") -> "QuerySet[UserMessage]":
        if self.value() == "0":
            return queryset.expired()
        if self.value() == "1":
            return queryset.active()
        return queryset


class UserDistributionListFilter(SimpleListFilter):
    parameter_name = "dl"
    title = _("Distribution List")
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[User]") -> list[tuple[str, str]]:
        from bitcaster.models import DistributionList

        return list(DistributionList.objects.all().values_list("id", "name"))

    def queryset(self, request: HttpRequest, queryset: "QuerySet[User]") -> "QuerySet[User]":
        if self.value():
            return queryset.filter(addresses__assignments__distributionlist__id=self.value()).distinct()
        return queryset


class AddressByList(SimpleListFilter):
    parameter_name = "dl"
    title = _("Distribution List")
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Address]|None") -> tuple[tuple[str, str], ...]:
        from bitcaster.models import DistributionList

        return tuple(DistributionList.objects.all().values_list("id", "name"))

    def queryset(self, request: HttpRequest, queryset: "QuerySet[Address]") -> "QuerySet[Address]":
        try:
            index = int(self.value() or 0)
            lookup_id = self.lookups(request, None)[index][0]
            return queryset.filter(assignments__distributionlist__id=lookup_id).distinct()
        except (ValueError, IndexError, TypeError):
            pass
        return queryset


class AddressByNotification(SimpleListFilter):
    parameter_name = "n"
    title = _("Notification")
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: "ModelAdmin[Address]|None") -> tuple[tuple[str, str], ...]:
        from bitcaster.models import Notification

        return tuple(Notification.objects.all().values_list("id", "name"))

    def queryset(self, request: HttpRequest, queryset: "QuerySet[Address]") -> "QuerySet[Address]":
        try:
            index = int(self.value() or 0)
            lookup_id = self.lookups(request, None)[index][0]
            return queryset.filter(assignments__distributionlist__notifications__id=lookup_id).distinct()
        except (ValueError, IndexError, TypeError):
            pass
        return queryset
