from django import forms
from django.contrib import admin

from bitcaster.constants import Bitcaster
from bitcaster.models import Organization, Project

from .fields import Select2TagField
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
    environments = Select2TagField(required=False)

    class Meta:
        model = Project
        exclude = ("config", "locked")

    def full_clean(self) -> None:
        return super().full_clean()


class ProjectAddForm(ProjectBaseForm):
    class Meta:
        model = Project
        exclude = ("channels", "locked")


class ProjectChangeForm(ProjectBaseForm):

    class Meta:
        model = Project
        exclude = ()
