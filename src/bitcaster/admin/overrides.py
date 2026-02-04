from constance.admin import Config
from django import forms
from django.http import HttpRequest
from flags.admin import FlagStateAdmin as _FlagStateAdmin
from flags.forms import FlagStateForm as BaseFlagStateForm
from flags.models import FlagState
from flags.state import flag_enabled
from unfold.contrib.filters.admin import RelatedDropdownFilter

from bitcaster.admin.base import BaseAdmin, BitcasterModelAdmin
from bitcaster.forms import unfold as uwidgets
from bitcaster.models import LogEntry

__all__ = ["Config", "FlagStateAdmin", "FlagState"]


class FlagStateForm(BaseFlagStateForm):
    name = forms.ChoiceField(label="Flag", required=True, widget=uwidgets.UnfoldAdminSelectWidget)
    condition = forms.ChoiceField(label="Condition name", required=True, widget=uwidgets.UnfoldAdminSelectWidget)
    value = forms.CharField(label="Expected value", required=True, widget=uwidgets.UnfoldAdminTextInputWidget)
    required = forms.BooleanField(
        label="Required",
        required=False,
        help_text=('All conditions marked "required" must be met to enable the flag'),
        widget=uwidgets.UnfoldBooleanSwitchWidget,
    )


class FlagStateAdmin(BaseAdmin, _FlagStateAdmin):
    search_fields = ("name",)
    list_display = ("name", "condition", "value", "required", "active")
    ordering = ("name",)
    list_filter = ("condition", "required")
    form = FlagStateForm

    def active(self, obj: FlagState) -> bool:
        return flag_enabled(obj.name)

    active.boolean = True


class LogEntryAdmin(BaseAdmin, BitcasterModelAdmin[LogEntry]):
    list_display = (
        "action_time",
        "user",
        "action_flag",
        "object_repr",
    )
    readonly_fields = ("user", "content_type", "object_id", "object_repr", "action_flag", "change_message")
    list_filter = (
        ("content_type", RelatedDropdownFilter),
        ("user", RelatedDropdownFilter),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
