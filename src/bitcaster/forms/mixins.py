from typing import TYPE_CHECKING, Any

from django import forms
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel  # noqa


class ScopedFormMixin(forms.ModelForm["AnyModel"]):

    def clean(self) -> dict[str, Any] | None:
        super().clean()
        if not self.cleaned_data.get("organization", None):
            raise forms.ValidationError(_("This field is required."))
        return self.cleaned_data
