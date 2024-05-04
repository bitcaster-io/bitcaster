from django import forms
from django.contrib import admin

from bitcaster.constants import Bitcaster
from bitcaster.models import Channel, Event, Organization

from .widgets import AutocompletSelectEnh


class ProjectBaseForm(forms.ModelForm["Project"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.exclude(name=Bitcaster.ORGANIZATION),
        required=True,
        widget=AutocompletSelectEnh(
            Channel._meta.get_field("organization"), admin.site, exclude={"name": Bitcaster.ORGANIZATION}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Event
        exclude = ("config", "locked")


class ProjectAddForm(ProjectBaseForm):
    class Meta:
        model = Event
        exclude = ("channels", "locked")


class ProjectChangeForm(ProjectBaseForm):

    class Meta:
        model = Event
        exclude = ()
