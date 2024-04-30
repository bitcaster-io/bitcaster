from typing import Any

from django import forms
from django.utils.translation import gettext as _


class ScopedFormMixin(forms.ModelForm):

    def clean(self) -> dict[str, Any] | None:
        super().clean()
        if not self.cleaned_data.get("organization", None):
            raise forms.ValidationError(_("This field is required."))
        return self.cleaned_data
