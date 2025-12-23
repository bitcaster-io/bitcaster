from django import forms

from bitcaster.models import Event


class EventBaseForm(forms.ModelForm["Event"]):
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
