from typing import Any

from django import forms
from django.contrib import admin
from django.forms import Field

from bitcaster.constants import bitcaster
from bitcaster.models import Application, Project

from .widgets import AutocompletSelectEnh


class ApplicationBaseForm(forms.ModelForm["Application"]):
    project = forms.ModelChoiceField(
        queryset=Project.objects.exclude(name=bitcaster.PROJECT),
        required=True,
        widget=AutocompletSelectEnh(
            Application._meta.get_field("project"), admin.site, exclude={"name": bitcaster.PROJECT}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Application
        exclude = ("config", "locked")  # noqa: DJ006


class ApplicationChangeForm(ApplicationBaseForm):
    class Meta:
        model = Application
        exclude = ()  # noqa: DJ006

    def get_initial_for_field(self, field: Field, field_name: str) -> Any:
        if field_name == "project":
            return Project.objects.local().first()
        return super().get_initial_for_field(field, field_name)
