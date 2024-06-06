from typing import TYPE_CHECKING

from django import forms
from django.db.models import TextChoices

from bitcaster.models import Channel, Organization

if TYPE_CHECKING:
    from bitcaster.web.wizards import LockingWizard


# 1. Lock by Channel, Project/Application/Event, User


class LockingModeChoice(TextChoices):
    CHANNEL = "CHANNEL", "by Channel"
    PROJECT = "PROJECT", "by Project"
    USER = "USER", "by User"


class ModeChoiceForm(forms.Form):
    step_header = "Select the criteria for locking"

    operation = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=LockingModeChoice,
    )


class LockingChannelForm(forms.Form):
    step_header = "Select the channels to lock"

    channel = forms.MultipleChoiceField(
        choices=[], required=False, help_text="Channels already locked will not show up"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        channels = Channel.objects.filter(locked=False, organization__in=Organization.objects.local()).all()
        choices = [(str(c.id), f"{c.name}{' (inactive)' if not c.active else ''}") for c in channels]
        self.fields["channel"] = forms.MultipleChoiceField(choices=choices)

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.CHANNEL:
            return True
        return False


class LockingUserForm(forms.Form):
    id = forms.CharField()

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.USER:
            return True
        return False


class LockingProjectForm(forms.Form):
    id = forms.CharField()

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.PROJECT:
            return True
        return False
