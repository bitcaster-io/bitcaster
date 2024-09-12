from typing import Any

from django import forms
from django.contrib import admin
from django.forms import Field

from bitcaster.constants import Bitcaster
from bitcaster.models import Application, Project

from .widgets import AutocompletSelectEnh


class ApplicationBaseForm(forms.ModelForm["Application"]):
    project = forms.ModelChoiceField(
        queryset=Project.objects.exclude(name=Bitcaster.PROJECT),
        required=True,
        widget=AutocompletSelectEnh(
            Application._meta.get_field("project"), admin.site, exclude={"name": Bitcaster.PROJECT}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Application
        exclude = ("config", "locked")


class ApplicationChangeForm(ApplicationBaseForm):
    class Meta:
        model = Application
        exclude = ()

    def get_initial_for_field(self, field: Field, field_name: str) -> Any:
        if field_name == "project":
            return Project.objects.local().first()
        return super().get_initial_for_field(field, field_name)
