from typing import Any

from os.path import splitext

from django import forms

from bitcaster.models import MediaFile


class MediaFileForm(forms.ModelForm["MediaFile"]):
    slug = forms.SlugField(required=False)

    class Meta:
        model = MediaFile
        fields = "__all__"  # noqa: DJ007

    def clean(self) -> dict[str, Any] | None:
        if img := self.cleaned_data.get("image"):
            self.cleaned_data["file_type"] = splitext(img.name)[1]
        return self.cleaned_data
