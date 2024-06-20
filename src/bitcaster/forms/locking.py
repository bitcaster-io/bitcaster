from typing import TYPE_CHECKING, Any

from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext as _

from bitcaster.models import Application, Channel, Organization, Project, User

if TYPE_CHECKING:
    from django.forms import Form

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

    def __init__(self, *args: Any, **kwargs: Any) -> "Form":
        self.storage = kwargs.pop("storage", None)
        super().__init__(*args, **kwargs)


class LockingChannelForm(forms.Form):
    channel = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Channel.objects.all(),
        help_text=_("Select the Channels to lock."),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> "Form":
        self.storage = kwargs.pop("storage", None)
        super().__init__(*args, **kwargs)
        self.fields["channel"].queryset = Channel.objects.filter(
            locked=False, organization__in=Organization.objects.local()
        ).all()

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.CHANNEL:
            return True
        return False


class LockingUserForm(forms.Form):
    user = forms.ModelChoiceField(
        empty_label=_("All"),
        required=False,
        queryset=User.objects.exclude(locked=True).all(),
        help_text=_("Select the user you want to lock"),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> "Form":
        self.storage = kwargs.pop("storage", None)
        super().__init__(*args, **kwargs)

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

    def __init__(self, *args: Any, **kwargs: Any) -> forms.Form:
        self.storage = kwargs.pop("storage", None)
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(
            locked=False, organization__in=Organization.objects.local()
        ).all()

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

    def __init__(self, *args: Any, **kwargs: Any) -> forms.Form:
        self.storage = kwargs.pop("storage", None)
        super().__init__(*args, **kwargs)
        project = self.storage["step_data"]["project"]["project-project"][0]
        if project:
            self.fields["application"].queryset = Application.objects.exclude(locked=True).filter(
                project_id=int(project)
            )
        else:
            self.fields["application"].queryset = Application.objects.exclude(locked=True).filter(
                project__organization__in=Organization.objects.local()
            )

    @staticmethod
    def visible(w: "LockingWizard") -> bool:
        if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == LockingModeChoice.PROJECT:
            return True
        return False
