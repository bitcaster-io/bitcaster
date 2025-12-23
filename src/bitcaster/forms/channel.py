from typing import Any

from django import forms

from bitcaster.forms.mixins import Scoped2FormMixin
from bitcaster.models import Channel, Organization

from .unfold import UnfoldAdminSelect2Widget


class ChannelBaseForm(forms.ModelForm["Channel"]):
    class Meta:
        model = Channel
        fields = ("organization", "project", "name", "dispatcher", "active", "parent")


class ChannelChangeForm(Scoped2FormMixin[Channel], ChannelBaseForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.local(), widget=UnfoldAdminSelect2Widget)

    class Meta:
        model = Channel
        fields = ("organization", "project", "name", "dispatcher", "active", "parent")

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        project = self.cleaned_data.get("project")
        organization = self.cleaned_data.get("organization")
        parent = self.cleaned_data.get("parent")
        if organization and project and organization.pk != project.organization.pk:
            self.add_error("project", "Project does not belong selected organization.")
        if parent and organization.pk != parent.organization.pk:
            self.add_error("parent", "Parent does not belong same organization.")

        return cleaned_data  # type: ignore[return-value]
