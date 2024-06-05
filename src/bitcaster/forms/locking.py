from typing import TYPE_CHECKING

from django import forms
from django.db.models import TextChoices

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
    step_header = "Select the channels to lock/unlock"

    channel = forms.MultipleChoiceField(
        choices=[],
    )

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.CHANNEL:
            return True
        return False


class LockingUserForm1(forms.Form):
    id = forms.CharField()


class LockingProjectForm1(forms.Form):
    id = forms.CharField()
