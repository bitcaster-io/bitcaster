from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from bitcaster.forms.mixins import ScopedFormMixin
from bitcaster.models import Application, Channel, Event


class EventBaseForm(ScopedFormMixin, forms.ModelForm["Channel"]):
    application = forms.ModelChoiceField(
        queryset=Application.objects.all(),
        required=False,
        widget=AutocompleteSelect(Channel._meta.get_field("application"), admin.site),
    )
    slug = forms.SlugField(
        required=False,
    )

    class Meta:
        model = Event
        exclude = ("config", "locked")

    def clean(self) -> dict[str, Any] | None:
        super().clean()
        if not self.instance.pk:
            if self.cleaned_data.get("application"):
                self.cleaned_data["project"] = self.cleaned_data["application"].project
            if self.cleaned_data.get("project"):
                self.cleaned_data["organization"] = self.cleaned_data["project"].organization
        return self.cleaned_data


class EventAddForm(EventBaseForm):
    class Meta:
        model = Event
        exclude = ("channels", "locked")


class EventChangeForm(EventBaseForm):

    class Meta:
        model = Event
        exclude = ()
