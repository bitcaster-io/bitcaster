from django import forms

from bitcaster.forms.mixins import Scoped2FormMixin
from bitcaster.models import Channel


class ChannelBaseForm(forms.ModelForm["Channel"]):
    class Meta:
        model = Channel
        exclude = ("config", "locked")


class ChannelChangeForm(Scoped2FormMixin[Channel], ChannelBaseForm):
    class Meta:
        model = Channel
        exclude = ("config", "locked")
