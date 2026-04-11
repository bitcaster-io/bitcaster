# mypy: disable-error-code="assignment"
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from bitcaster.models import Event, Notification, User
from bitcaster.models.choices import FILTERING_DYNAMIC, FILTERING_EXTERNAL, FILTERING_NONE
from bitcaster.utils.filtering import validate_filters, validate_lookups, validate_schema


class NotificationForm(forms.ModelForm["Notification"]):
    class Meta:
        model = Notification
        exclude = ("config", "locked")  # noqa: DJ006

    def clean(self) -> dict[str, Any]:
        evt: Event
        prj_envs: list[str] = []
        envs: list[str] = []
        super().clean()
        policy = self.cleaned_data.get("policy", None)
        if policy == FILTERING_DYNAMIC:
            self.cleaned_data["distribution"] = None
            try:
                recipients = self.cleaned_data.get("recipients_filter", {"include": [], "exclude": []})
                validate_schema(recipients)
                validate_filters(User.objects, recipients)
                validate_lookups(User, recipients)
            except ValidationError as e:
                raise ValidationError({"recipients_filter": e}) from None

        # if self.cleaned_data.get("external_filtering", False):
        elif policy == FILTERING_EXTERNAL:
            self.cleaned_data["distribution"] = None

        elif (
            self.instance.pk
            and self.cleaned_data["active"]
            and (policy == FILTERING_NONE and not self.cleaned_data.get("distribution"))
        ):
            raise ValidationError({"distribution": "This field is required"}) from None

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
