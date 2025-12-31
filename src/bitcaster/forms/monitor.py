from django import forms

from bitcaster.forms.unfold import UnfoldForm
from bitcaster.models import Monitor


class MonitorForm(UnfoldForm, forms.ModelForm["Monitor"]):
    class Meta:
        model = Monitor
        exclude = ("config", "data")  # noqa: DJ006
