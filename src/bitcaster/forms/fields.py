from django import forms

from bitcaster.forms.widgets import EnvironmentWidget


class Select2TagField(forms.CharField):
    widget = EnvironmentWidget

    def to_python(self, value):
        ret = super().to_python(value)
        return ret.split(",")

    def clean(self, value: str) -> list:
        if value:
            value = value.split(",")
        else:
            value = []
        return value
