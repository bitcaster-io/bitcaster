from typing import Any

from django import forms

from bitcaster.forms.widgets import EnvironmentWidget


class Select2TagField(forms.Field):
    widget = EnvironmentWidget

    def to_python(self, value: Any) -> list[str]:
        ret = super().to_python(value)
        return ret.split(",")

    def clean(self, value: str) -> list[str]:
        if value:
            return value.split(",")
        return []
