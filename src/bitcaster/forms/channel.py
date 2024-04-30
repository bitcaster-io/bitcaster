from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from bitcaster.forms.mixins import ScopedFormMixin
from bitcaster.models import Application, Channel, Organization, Project


class ChannelBaseForm(forms.ModelForm["Channel"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=AutocompleteSelect(Channel._meta.get_field("organization"), admin.site),
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        widget=AutocompleteSelect(Channel._meta.get_field("project"), admin.site),
    )
    application = forms.ModelChoiceField(
        queryset=Application.objects.all(),
        required=False,
        widget=AutocompleteSelect(Channel._meta.get_field("application"), admin.site),
    )

    class Meta:
        model = Channel
        exclude = ("config", "locked")

    def clean(self) -> dict[str, Any] | None:
        if self.cleaned_data["application"]:
            self.cleaned_data["project"] = self.cleaned_data["application"].project
        if self.cleaned_data["project"]:
            self.cleaned_data["organization"] = self.cleaned_data["project"].organization
        return self.cleaned_data


class ChannelAddForm(ScopedFormMixin, ChannelBaseForm):
    class Meta:
        model = Channel
        exclude = ("config", "locked")


class ChannelChangeForm(ScopedFormMixin, ChannelBaseForm):

    class Meta:
        model = Channel
        exclude = ("config", "locked")
