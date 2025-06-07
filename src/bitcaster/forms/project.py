from django import forms
from django.contrib import admin

from bitcaster.constants import bitcaster
from bitcaster.models import Organization, Project

from .fields import Select2TagField
from .widgets import AutocompletSelectEnh


class ProjectBaseForm(forms.ModelForm["Project"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.exclude(name=bitcaster.ORGANIZATION),
        required=True,
        widget=AutocompletSelectEnh(
            Project._meta.get_field("organization"), admin.site, exclude={"name": bitcaster.ORGANIZATION}
        ),
    )
    slug = forms.SlugField(required=False)
    environments = Select2TagField(required=False)

    class Meta:
        model = Project
        exclude = ("config", "locked")  # noqa: DJ006

    def full_clean(self) -> None:
        return super().full_clean()


class ProjectAddForm(ProjectBaseForm):
    class Meta:
        model = Project
        exclude = ("channels", "locked")  # noqa: DJ006


class ProjectChangeForm(ProjectBaseForm):
    class Meta:
        model = Project
        exclude = ()
