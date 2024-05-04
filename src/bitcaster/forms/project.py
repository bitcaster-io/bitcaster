from django import forms
from django.contrib import admin

from bitcaster.constants import Bitcaster
from bitcaster.models import Organization, Project

from .widgets import AutocompletSelectEnh


class ProjectBaseForm(forms.ModelForm["Project"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.exclude(name=Bitcaster.ORGANIZATION),
        required=True,
        widget=AutocompletSelectEnh(
            Project._meta.get_field("organization"), admin.site, exclude={"name": Bitcaster.ORGANIZATION}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Project
        exclude = ("config", "locked")


class ProjectAddForm(ProjectBaseForm):
    class Meta:
        model = Project
        exclude = ("channels", "locked")


class ProjectChangeForm(ProjectBaseForm):

    class Meta:
        model = Project
        exclude = ()
