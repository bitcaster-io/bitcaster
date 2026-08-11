from typing import TYPE_CHECKING, Any, cast

import logging

from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import link
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.forms import TypedChoiceField
from django.urls import URLPattern, path, reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import bitcaster
from bitcaster.forms.unfold import UnfoldAdminSelect2Widget
from bitcaster.models import User
from bitcaster.utils.django import admin_toggle_bool_action
from bitcaster.web.dashboard.views import LockView, MonitorView, SanityView, ToolsView

from .base import BaseAdmin

if TYPE_CHECKING:
    from django.db.models import Field, QuerySet
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class UserAdmin(BaseAdmin[User], DjangoUserAdmin[User]):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    exclude = ("groups",)
    fieldsets = (
        (_("Personal info"), {"classes": ["tab"], "fields": ("first_name", "last_name", "email")}),
        (_("Account"), {"classes": ["tab"], "fields": ("username", "password")}),
        (
            _("Permissions"),
            {
                "classes": ["tab"],
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"classes": ["tab"], "fields": ("last_login", "date_joined")}),
        (_("Options"), {"classes": ["tab"], "fields": ("timezone", "date_format", "time_format")}),
        (_("Extended"), {"classes": ["tab"], "fields": ("custom_fields",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "usable_password"),
            },
        ),
    )
    filter_horizontal = ()
    change_user_password_template = "admin/auth/user/change_password.html"  # nosec  # noqa: S105
    actions = ["toggle_superuser", "toggle_staff", "toggle_active", "enroll"]

    def get_readonly_fields(self, request: "HttpRequest", obj: "User | None" = None) -> list[str]:
        return ["custom_fields"]

    def formfield_for_choice_field(
        self, db_field: "Field[Any, Any]", request: "HttpRequest", **kwargs: Any
    ) -> TypedChoiceField:
        if db_field.name == "timezone":
            return TypedChoiceField(choices=list(db_field.choices or []), coerce=str, widget=UnfoldAdminSelect2Widget)
        return cast("TypedChoiceField", super().formfield_for_choice_field(db_field, request, **kwargs))

    def delete_model(self, request: "HttpRequest", obj: User) -> None:
        super().delete_model(request, obj)

    def delete_queryset(self, request: "HttpRequest", queryset: "QuerySet[User]") -> None:
        super().delete_queryset(request, queryset)

    def get_urls(self) -> list[URLPattern]:
        extra = []
        for console in [ToolsView, LockView, MonitorView, SanityView]:
            custom_view = self.admin_site.admin_view(console.as_view(model_admin=self))
            extra.append(
                path(console.__name__.lower(), custom_view, name=f"console-{console.__name__.lower()}"),
            )
        return super().get_urls() + extra

    def toggle_superuser(self, request: "HttpRequest", queryset: "QuerySet[User]") -> None:
        admin_toggle_bool_action(request, queryset.exclude(pk=request.user.pk), "is_superuser")

    def toggle_staff(self, request: "HttpRequest", queryset: "QuerySet[User]") -> None:
        admin_toggle_bool_action(request, queryset.exclude(pk=request.user.pk), "is_staff")

    def enroll(self, request: "HttpRequest", queryset: "QuerySet[User]") -> None:
        bitcaster.local_organization.enroll_users(queryset)

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def addresses(self, button: StandardButton) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_address_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?user__exact={user.pk}"

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def lists(self, button: StandardButton) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_distributionlist_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?recipients__address__user__exact={user.pk}"

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def notifications(self, button: StandardButton) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_notification_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?distribution__recipients__address__user={user.pk}"

    @link(change_form=True, change_list=False)  # type: ignore[arg-type]
    def events(self, button: StandardButton) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_event_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?notifications__distribution__recipients__address__user__exact={user.pk}"
