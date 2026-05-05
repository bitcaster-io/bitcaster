from typing import Any

from django import forms
from django.forms import Field

from bitcaster.constants import bitcaster
from bitcaster.models import Application, Project

from . import unfold


class ApplicationBaseForm(forms.ModelForm["Application"]):
    project = forms.ModelChoiceField(
        queryset=Project.objects.exclude(name=bitcaster.PROJECT), required=True, widget=unfold.UnfoldAdminSelect2Widget
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Application
        exclude = ("config", "locked")  # noqa: DJ006


class ApplicationChangeForm(ApplicationBaseForm):
    class Meta:
        model = Application
        exclude = ("advanced_configuration",)  # noqa: DJ006

    def get_initial_for_field(self, field: Field, field_name: str) -> Any:
        if field_name == "project":
            return Project.objects.local().first()
        return super().get_initial_for_field(field, field_name)


class ApplicationAdvancedConfigForm(forms.Form):
    support_attachments = forms.BooleanField(required=False)
