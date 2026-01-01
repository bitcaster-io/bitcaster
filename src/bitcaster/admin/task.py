from typing import TYPE_CHECKING, Any

from admin_extra_buttons.decorators import button
from django.db.models import Model
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from jsoneditor.forms import JSONEditor

from bitcaster.models import LogEntry, Task

from ..forms.task import TaskAddForm, TaskForm
from .base import BaseAdmin, UnfoldModelAdmin

if TYPE_CHECKING:
    from django import forms


class TaskAdmin(BaseAdmin, UnfoldModelAdmin[Task]):
    list_display = ("name", "func", "scheduling", "active")
    form = TaskForm
    add_fieldsets = (
        (
            _("General"),
            {
                "classes": ["tab"],
                "fields": ["name", "slug", "func", "args", "kwargs"],
            },
        ),
    )
    fieldsets = (
        (
            _("General"),
            {"classes": ["tab"], "fields": ["name", "slug", "active", "last_updated", "func", "args", "kwargs"]},
        ),
        (_("Job"), {"classes": ["tab"], "fields": ["replace_existing", "max_instances", "next_run_time"]}),
        (_("trigger"), {"classes": ["tab"], "fields": ["trigger", "trigger_config"]}),
    )

    def get_form(
        self, request: "HttpRequest", obj: "Model | None" = None, change: bool = False, **kwargs: Any
    ) -> "type[forms.ModelForm[Task]]":
        if change:
            self.form = TaskForm
        else:
            self.form = TaskAddForm
        return super().get_form(request, obj, change, **kwargs)

    @button(visible=lambda b: b.context["original"].active)
    def pause(self, request, pk) -> None:
        qs = self.get_queryset(request).filter(pk=pk)
        qs.update(active=False, last_updated=timezone.now())
        LogEntry.objects.log_actions(request.user.id, qs, LogEntry.CHANGE, "Paused")

    @button(visible=lambda b: not b.context["original"].active)
    def resume(self, request, pk) -> None:
        qs = self.get_queryset(request).filter(pk=pk)
        qs.update(active=True, last_updated=timezone.now())
        LogEntry.objects.log_actions(request.user.id, qs, LogEntry.CHANGE, "Resumed")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ["args", "kwargs", "trigger_config"]:
            field.widget = JSONEditor()
        return field

    def get_readonly_fields(self, request, obj: Model | None = None) -> list[str]:
        if obj and obj.pk:
            return ["slug", "active", "last_updated"]
        return super().get_readonly_fields(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(
            reverse(
                f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
                args=[obj.pk],
            )
        )
