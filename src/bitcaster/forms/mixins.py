from typing import TYPE_CHECKING

from django import forms
from django_select2 import forms as s2forms
from unfold import widgets as uwidgets

from bitcaster.models import Application, Organization

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel  # noqa


class Scoped2FormMixin(forms.ModelForm["AnyModel"]):
    # pass
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(), required=True, widget=uwidgets.UnfoldAdminSelect2Widget
    )
    # project = ChainedModelChoiceField(
    #     to_app_name="bitcaster",
    #     to_model_name="project",
    #     chained_field="organization",
    #     chained_model_field="organization",
    #     foreign_key_app_name="bitcaster",
    #     foreign_key_model_name="organization",
    #     foreign_key_field_name="organization",
    #     show_all=False,
    #     auto_choose=False,
    # )
    # organization = forms.ModelChoiceField(
    #     queryset=Organization.objects.all(),
    #     label="Organization",
    #     widget=s2forms.ModelSelect2Widget(
    #         model=Organization,
    #         search_fields=["name__icontains"],
    #     ),
    # )
    #
    # project = forms.ModelChoiceField(
    #     required=False,
    #     queryset=Project.objects.all(),
    #     label="Project",
    #     widget=s2forms.ModelSelect2Widget(
    #         model=Project,
    #         search_fields=["name__icontains"],
    #         dependent_fields={"organization": "organization"},
    #         max_results=500,
    #     ),
    # )


class Scoped3FormMixin(Scoped2FormMixin["AnyModel"]):
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
