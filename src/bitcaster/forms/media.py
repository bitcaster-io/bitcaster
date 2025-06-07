from os.path import splitext
from typing import Any

from django import forms
from django.contrib import admin

from bitcaster.constants import bitcaster
from bitcaster.models import Application, MediaFile, Organization, Project

from .widgets import AutocompletSelectEnh


class MediaFileForm(forms.ModelForm["MediaFile"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.exclude(name=bitcaster.PROJECT),
        required=True,
        widget=AutocompletSelectEnh(
            MediaFile._meta.get_field("project"), admin.site, exclude={"name": bitcaster.ORGANIZATION}
        ),
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.exclude(name=bitcaster.PROJECT),
        required=True,
        widget=AutocompletSelectEnh(
            MediaFile._meta.get_field("project"), admin.site, exclude={"name": bitcaster.PROJECT}
        ),
    )
    application = forms.ModelChoiceField(
        queryset=Application.objects.exclude(name=bitcaster.PROJECT),
        required=True,
        widget=AutocompletSelectEnh(
            MediaFile._meta.get_field("application"), admin.site, exclude={"name": bitcaster.APPLICATION}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = MediaFile
        fields = "__all__"  # noqa: DJ007

    def clean(self) -> dict[str, Any] | None:
        self.cleaned_data["file_type"] = splitext(self.cleaned_data["image"].name)[1]
        return self.cleaned_data
