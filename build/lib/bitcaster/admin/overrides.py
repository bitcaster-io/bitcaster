from json import loads
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from constance.admin import Config
from constance.admin import ConstanceAdmin as _ConstanceAdmin
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django_celery_beat.admin import PeriodicTaskAdmin as _PeriodicTaskAdmin
from django_celery_beat.models import PeriodicTask
from flags.admin import FlagStateAdmin as _FlagStateAdmin
from flags.models import FlagState
from flags.state import flag_enabled

if TYPE_CHECKING:
    from django.http import HttpResponse

__all__ = ["ConstanceAdmin", "Config", "FlagStateAdmin", "FlagState", "PeriodicTask", "PeriodicTaskAdmin"]


class ConstanceAdmin(_ConstanceAdmin):
    pass


class FlagStateAdmin(_FlagStateAdmin):
    search_fields = ("name",)
    list_display = ("name", "condition", "value", "required", "active")
    ordering = ("name",)
    list_filter = ("condition", "required")

    def active(self, obj: FlagState) -> bool:
        return flag_enabled(obj.name)

    active.boolean = True


class PeriodicTaskAdmin(ExtraButtonsMixin, _PeriodicTaskAdmin):
    @button()
    def run(self, request: HttpRequest, pk: str) -> "HttpResponse":
        pt = PeriodicTask.objects.get(pk=pk)
        task = self.celery_app.tasks.get(pt.task)
        if task:  # pragma: no branch
            task.apply_async(args=loads(pt.args), kwargs=loads(pt.kwargs), queue=pt.queue, periodic_task_name=pt.name)
            self.message_user(request, _("{0} task was successfully queued").format(pt.name))
