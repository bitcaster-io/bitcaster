from django import forms

from bitcaster.models import Monitor


class MonitorForm(forms.ModelForm["Monitor"]):
    class Meta:
        model = Monitor
        exclude = ("config", "data")  # noqa: DJ006
