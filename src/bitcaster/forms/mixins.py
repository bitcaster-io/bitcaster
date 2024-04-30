from typing import TYPE_CHECKING, Any

from django import forms
from django.utils.translation import gettext as _
from django_select2 import forms as s2forms

from bitcaster.models import Application, Organization, Project

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel  # noqa


class ScopedFormMixin(forms.ModelForm["AnyModel"]):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        label="Organization",
        widget=s2forms.ModelSelect2Widget(
            model=Organization,
            search_fields=["name__icontains"],
        ),
    )

    project = forms.ModelChoiceField(
        required=False,
        queryset=Project.objects.all(),
        label="Project",
        widget=s2forms.ModelSelect2Widget(
            model=Project,
            search_fields=["name__icontains"],
            dependent_fields={"organization": "organization"},
            max_results=500,
        ),
    )
    application = forms.ModelChoiceField(
        required=False,
        queryset=Application.objects.all(),
        label="Application",
        widget=s2forms.ModelSelect2Widget(
            model=Application,
            search_fields=["name__icontains"],
            dependent_fields={"project": "project"},
            max_results=500,
        ),
    )

    def clean(self) -> dict[str, Any] | None:
        super().clean()
        if not self.cleaned_data.get("organization", None):
            raise forms.ValidationError(_("This field is required."))
        return self.cleaned_data
