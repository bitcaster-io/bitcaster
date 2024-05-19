from typing import Any

from django import forms

from bitcaster.forms.mixins import Scoped2FormMixin
from bitcaster.models import Channel


class ChannelBaseForm(forms.ModelForm["Channel"]):
    class Meta:
        model = Channel
        exclude = ("config", "locked")

    def clean(self) -> dict[str, Any] | None:
        if self.cleaned_data["project"]:
            self.cleaned_data["organization"] = self.cleaned_data["project"].organization
        return self.cleaned_data


class ChannelChangeForm(Scoped2FormMixin[Channel], ChannelBaseForm):

    class Meta:
        model = Channel
        exclude = ("config", "locked")
