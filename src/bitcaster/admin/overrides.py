from json import loads
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.decorators import button
from constance.admin import Config
from django import forms
from django.db.models import Field
from django.forms import TypedChoiceField
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django_celery_beat.admin import PeriodicTaskAdmin as _PeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm as _PeriodicTaskForm
from django_celery_beat.admin import TaskChoiceField, TaskSelectWidget
from django_celery_beat.models import PeriodicTask
from flags.admin import FlagStateAdmin as _FlagStateAdmin
from flags.forms import FlagStateForm as BaseFlagStateForm
from flags.models import FlagState
from flags.state import flag_enabled
from jsoneditor.forms import JSONEditor
from unfold.contrib.filters.admin import RelatedDropdownFilter

from bitcaster.admin.base import BaseAdmin, BitcasterModelAdmin
from bitcaster.forms import unfold as uwidgets
from bitcaster.models import LogEntry

if TYPE_CHECKING:
    from django.http import HttpResponse

__all__ = ["Config", "FlagStateAdmin", "FlagState", "PeriodicTask", "PeriodicTaskAdmin"]


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


class UnfoldTaskSelectWidget(uwidgets.UnfoldAdminSelectWidget, TaskSelectWidget):
    template_name = "unfold/widgets/select.html"


class PeriodicTaskForm(_PeriodicTaskForm):
    regtask = TaskChoiceField(
        label=_("Task (registered)"),
        required=False,
        widget=UnfoldTaskSelectWidget,
    )
    task = forms.CharField(
        label=_("Task (custom)"),
        required=False,
        max_length=200,
        widget=uwidgets.UnfoldAdminTextInputWidget,
    )


class PeriodicTaskAdmin(BaseAdmin, _PeriodicTaskAdmin):
    form = PeriodicTaskForm
    fieldsets = (
        (_("General"), {"classes": ["tab"], "fields": ["name", "task", "regtask", "enabled", "description"]}),
        (_("Schedule"), {"classes": ["tab"], "fields": ["interval", "crontab", "solar", "clocked"]}),
        (_("Arguments"), {"classes": ["tab"], "fields": ["args", "kwargs"]}),
        (_("Advanced"), {"classes": ["tab"], "fields": ["queue", "exchange", "routing_key", "headers", "priority"]}),
        (_("Date/Time"), {"classes": ["tab"], "fields": ["expires", "expire_seconds", "one_off", "start_time"]}),
        (_("Infos"), {"classes": ["tab"], "fields": ["last_run_at", "total_run_count", "date_changed"]}),
    )
    readonly_fields = ("total_run_count", "last_run_at", "date_changed")

    @button()
    def run(self, request: HttpRequest, pk: str) -> "HttpResponse":
        pt = PeriodicTask.objects.get(pk=pk)
        task = self.celery_app.tasks.get(pt.task)
        if task:  # pragma: no branch
            task.apply_async(args=loads(pt.args), kwargs=loads(pt.kwargs), queue=pt.queue, periodic_task_name=pt.name)
            self.message_user(request, _("{0} task was successfully queued").format(pt.name))

    def formfield_for_choice_field(self, db_field: Field, request: HttpRequest, **kwargs) -> TypedChoiceField:
        formfield = super().formfield_for_choice_field(db_field, request, **kwargs)
        if db_field.name == "regtask":
            formfield.widget = uwidgets.UnfoldAdminTextInputWidget()

        return formfield

    def formfield_for_dbfield(self, db_field: Field, request: HttpRequest, **kwargs: Any) -> Field | None:
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ["args", "kwargs"]:
            formfield.widget = JSONEditor()
        elif db_field.name == "task":
            formfield.widget = uwidgets.UnfoldAdminTextInputWidget()

        return formfield


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
