from django import forms
from django.contrib import admin

from bitcaster.constants import Bitcaster
from bitcaster.models import Application, Project

from .widgets import AutocompletSelectEnh


class ApplicationBaseForm(forms.ModelForm["Project"]):
    project = forms.ModelChoiceField(
        queryset=Project.objects.exclude(name=Bitcaster.PROJECT),
        required=True,
        widget=AutocompletSelectEnh(
            Application._meta.get_field("project"), admin.site, exclude={"name": Bitcaster.PROJECT}
        ),
    )
    slug = forms.SlugField(required=False)

    class Meta:
        model = Application
        exclude = ("config", "locked")


class ApplicationAddForm(ApplicationBaseForm):
    class Meta:
        model = Application
        exclude = ("channels", "locked")


class ApplicationChangeForm(ApplicationBaseForm):

    class Meta:
        model = Application
        exclude = ()
