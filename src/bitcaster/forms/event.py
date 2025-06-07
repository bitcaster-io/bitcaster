from django import forms
from django.contrib import admin

from bitcaster.constants import bitcaster
from bitcaster.forms.widgets import AutocompletSelectEnh
from bitcaster.models import Application, Event


class EventBaseForm(forms.ModelForm["Event"]):
    application = forms.ModelChoiceField(
        queryset=Application.objects.exclude(name=bitcaster.APPLICATION),
        required=True,
        widget=AutocompletSelectEnh(
            Event._meta.get_field("application"), admin.site, exclude={"name": bitcaster.APPLICATION}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Event
        exclude = ("config", "locked")  # noqa: DJ006


class EventAddForm(EventBaseForm):
    class Meta:
        model = Event
        exclude = ("channels", "locked")  # noqa: DJ006


class EventChangeForm(EventBaseForm):
    class Meta:
        model = Event
        exclude = ()  # noqa: DJ006
