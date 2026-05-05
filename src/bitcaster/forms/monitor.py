from django import forms

from bitcaster.models import Monitor

from .unfold import UnfoldForm


class MonitorForm(UnfoldForm, forms.ModelForm["Monitor"]):
    class Meta:
        model = Monitor
        exclude = ("config", "data")  # noqa: DJ006
