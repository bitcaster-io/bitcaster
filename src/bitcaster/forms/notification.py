# mypy: disable-error-code="assignment"
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from bitcaster.models import Event, Notification

from .fields import Select2TagField


class NotificationForm(forms.ModelForm["Notification"]):
    environments = Select2TagField(required=False)

    class Meta:
        model = Notification
        exclude = ("config", "locked")  # noqa: DJ006

    def clean(self) -> dict[str, Any]:
        evt: Event
        prj_envs: list[str] = []
        envs: list[str] = []
        super().clean()
        if self.instance.pk:
            evt = self.instance.event
            prj_envs = evt.application.project.environments or []
            envs = self.cleaned_data.get("environments", [])
        elif evt := self.cleaned_data.get("event"):
            prj_envs = evt.application.project.environments or []
            envs = self.cleaned_data.get("environments", [])
        if not set(envs).issubset(prj_envs):
            raise ValidationError({"environments": "One or more values are not available in the project"})
        return self.cleaned_data
