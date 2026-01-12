import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import link
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.forms import TypedChoiceField
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from bitcaster.forms.unfold import UnfoldAdminSelect2Widget
from bitcaster.web.dashboard.views import LockView, MonitorView, ToolsView

from ..constants import bitcaster
from ..models import User
from ..utils.django import admin_toggle_bool_action
from .base import BaseAdmin, BitcasterModelAdmin

if TYPE_CHECKING:
    from django.db.models import Field, QuerySet
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class UserAdmin(BaseAdmin, BitcasterModelAdmin, DjangoUserAdmin[User]):
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
    filter_horizontal = ()
    change_user_password_template = "admin/auth/user/change_password2.html"  # nosec  # noqa: S105
    actions = ["toggle_superuser", "toggle_staff", "toggle_active", "enroll"]

    def get_readonly_fields(self, request: "HttpRequest", obj: "User|None" = None) -> list[str]:
        return ["custom_fields"]

    def formfield_for_choice_field(self, db_field: "Field", request: "HttpRequest", **kwargs) -> TypedChoiceField:
        if db_field.name == "timezone":
            return TypedChoiceField(choices=db_field.choices, coerce=str, widget=UnfoldAdminSelect2Widget)
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_urls(self):
        extra = []
        for console in [ToolsView, LockView, MonitorView]:
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

    @link(change_form=True, change_list=False)
    def addresses(self, button: ButtonWidget) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_address_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?user__exact={user.pk}"

    @link(change_form=True, change_list=False)
    def lists(self, button: ButtonWidget) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_distributionlist_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?recipients__address__user__exact={user.pk}"

    @link(change_form=True, change_list=False)
    def notifications(self, button: ButtonWidget) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_notification_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?distribution__recipients__address__user={user.pk}"

    @link(change_form=True, change_list=False)
    def events(self, button: ButtonWidget) -> None:
        url = reverse(f"{self.admin_site.name}:bitcaster_event_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?notifications__distribution__recipients__address__user__exact={user.pk}"
