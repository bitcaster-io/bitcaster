from typing import TYPE_CHECKING

from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext as _

from bitcaster.models import Application, Channel, Organization, Project

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
    channel = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Channel.objects.all(),
        help_text=_("Select the Channels to lock."),
    )

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
    project = forms.ModelChoiceField(
        empty_label=_("All"),
        required=False,
        queryset=Project.objects.all(),
        help_text=_("Select the project you want to lock"),
    )

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.PROJECT:
            return True
        return False


class LockingApplicationForm(forms.Form):
    application = forms.ModelChoiceField(
        empty_label=_("All"),
        required=False,
        queryset=Application.objects.all(),
        help_text=_("Select the application you want to lock"),
    )

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.PROJECT:
            return True
        return False
