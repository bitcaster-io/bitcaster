from json import loads
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from constance.admin import Config
from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django_celery_beat.admin import PeriodicTaskAdmin as _PeriodicTaskAdmin
from django_celery_beat.models import PeriodicTask
from flags.admin import FlagStateAdmin as _FlagStateAdmin
from flags.forms import FlagStateForm as BaseFlagStateForm
from flags.models import FlagState
from flags.state import flag_enabled
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget, UnfoldBooleanSwitchWidget

from bitcaster.admin.base import BaseAdmin

if TYPE_CHECKING:
    from django.http import HttpResponse

__all__ = ["Config", "FlagStateAdmin", "FlagState", "PeriodicTask", "PeriodicTaskAdmin"]


class FlagStateForm(BaseFlagStateForm):
    name = forms.ChoiceField(label="Flag", required=True, widget=UnfoldAdminSelectWidget)
    condition = forms.ChoiceField(label="Condition name", required=True, widget=UnfoldAdminSelectWidget)
    value = forms.CharField(label="Expected value", required=True, widget=UnfoldAdminTextInputWidget)
    required = forms.BooleanField(
        label="Required",
        required=False,
        help_text=('All conditions marked "required" must be met to enable the flag'),
        widget=UnfoldBooleanSwitchWidget,
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


class PeriodicTaskAdmin(BaseAdmin, _PeriodicTaskAdmin):
    @button()
    def run(self, request: HttpRequest, pk: str) -> "HttpResponse":
        pt = PeriodicTask.objects.get(pk=pk)
        task = self.celery_app.tasks.get(pt.task)
        if task:  # pragma: no branch
            task.apply_async(args=loads(pt.args), kwargs=loads(pt.kwargs), queue=pt.queue, periodic_task_name=pt.name)
            self.message_user(request, _("{0} task was successfully queued").format(pt.name))
