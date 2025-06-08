import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import link
from django.contrib.admin import helpers
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from ..forms.user import SelectDistributionForm
from ..models import Assignment, DistributionList, User
from .base import BaseAdmin

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class UserAdmin(BaseAdmin, DjangoUserAdmin[User]):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    exclude = ("groups",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    filter_horizontal = ()
    change_user_password_template = "admin/auth/user/change_password2.html"  # nosec  # noqa: S105
    actions = ["export_as_csv", "add_to_distributionlist"]

    def add_to_distributionlist(self, request: "HttpRequest", queryset: "QuerySet[User]") -> HttpResponse:
        ctx = self.get_common_context(request, title=_("Add to Distributionlist"))
        initial = {
            "_selected_action": request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
            "select_across": request.POST.get("select_across") == "1",
            "action": request.POST.get("action", ""),
        }
        if "apply" in request.POST:
            form = SelectDistributionForm(request.POST, request.FILES)
            if form.is_valid():
                dl: DistributionList = form.cleaned_data["dl"]
                for user in queryset:
                    if asm := Assignment.objects.filter(address__user=user).first():
                        dl.recipients.add(asm)
                self.message_user(request, _("Users successfully added"))
                return HttpResponseRedirect(reverse("admin:bitcaster_user_changelist"))
        else:
            form = SelectDistributionForm(initial=initial)
        ctx["form"] = form
        return TemplateResponse(request, "admin/bitcaster/user/add_to_distributionlist.html", ctx)

    @link(change_form=True, change_list=False)
    def addresses(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_address_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?user__exact={user.pk}"

    @link(change_form=True, change_list=False)
    def lists(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_distributionlist_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?recipients__address__user__exact={user.pk}"

    @link(change_form=True, change_list=False)
    def notifications(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_notification_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?distribution__recipients__address__user={user.pk}"

    @link(change_form=True, change_list=False)
    def events(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_event_changelist")
        user: User = button.context["original"]
        button.href = f"{url}?notifications__distribution__recipients__address__user__exact={user.pk}"
