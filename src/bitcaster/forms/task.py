from typing import TYPE_CHECKING, Any

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django import forms
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.utils.text import slugify

from bitcaster.models import Task
from bitcaster.runner.manager import BlockingScheduler

from .unfold import UnfoldAdminIntegerFieldWidget

if TYPE_CHECKING:
    from apscheduler.triggers.base import BaseTrigger


class TaskAddForm(forms.ModelForm[Task]):
    slug = forms.CharField(required=False)

    def clean_func(self) -> str | None:
        func = self.cleaned_data["func"]
        try:
            import_string(func)
        except ImportError:
            raise ValidationError("Invalid function name") from None
        return func

    class Meta:
        model = Task
        fields = (
            "name",
            "func",
        )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if (name := cleaned_data.get("name")) and not cleaned_data.get("slug"):
            self.cleaned_data["slug"] = slugify(name)
        return cleaned_data


class TaskForm(TaskAddForm):
    max_instances = forms.IntegerField(min_value=1, widget=UnfoldAdminIntegerFieldWidget)

    class Meta:
        model = Task
        fields = (
            "name",
            "func",
            "replace_existing",
            "max_instances",
            "next_run_time",
            "args",
            "kwargs",
            "trigger",
            "trigger_config",
            "active",
        )

    def clean_func(self) -> str | None:
        func = self.cleaned_data["func"]
        try:
            import_string(func)
        except ImportError:
            raise ValidationError("Invalid function name") from None
        return func

    def validate_job(self, cleaned_data: dict[str, Any]) -> None:
        kwargs = {k: v for k, v in cleaned_data.items() if k in Job.__slots__}
        kwargs["func"] = import_string(cleaned_data["func"])
        kwargs["trigger"] = self.validate_trigger(cleaned_data)
        scheduler = BlockingScheduler()
        job = scheduler.add_job(**kwargs)
        scheduler.remove_job(job.id)

    def validate_trigger(self, cleaned_data: dict[str, Any]) -> "BaseTrigger|None":
        trigger_class = None
        match cleaned_data.get("trigger"):
            case "interval":
                trigger_class = IntervalTrigger
            case "cron":
                trigger_class = CronTrigger
            case None:
                self.add_error("trigger", "Please select a valid trigger")
        if trigger_class:
            try:
                return trigger_class(**cleaned_data.get("trigger_config", {}))
            except (TypeError, ValueError) as e:
                self.add_error("trigger_config", str(e))
        return None

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if cleaned_data:
            self.validate_trigger(cleaned_data)
            self.validate_job(cleaned_data)
        return cleaned_data
