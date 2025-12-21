from os.path import splitext
from typing import Any

from django import forms

from bitcaster.models import MediaFile


class MediaFileForm(forms.ModelForm["MediaFile"]):
    slug = forms.SlugField(required=False)

    class Meta:
        model = MediaFile
        fields = "__all__"  # noqa: DJ007

    def clean(self) -> dict[str, Any] | None:
        self.cleaned_data["file_type"] = splitext(self.cleaned_data["image"].name)[1]
        return self.cleaned_data
