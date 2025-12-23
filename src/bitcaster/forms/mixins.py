from typing import TYPE_CHECKING

from django import forms
from unfold import widgets as uwidgets

from bitcaster.constants import bitcaster
from bitcaster.models import Application, Organization

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel_co  # noqa


class Scoped2FormMixin(forms.ModelForm["AnyModel_co"]):
    # pass
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.local(), required=True, widget=uwidgets.UnfoldAdminSelect2Widget
    )


class Scoped3FormMixin(Scoped2FormMixin["AnyModel_co"]):
    application = forms.ModelChoiceField(
        required=False,
        queryset=Application.objects.exclude(project__organization__name=bitcaster.ORGANIZATION),
        label="Application",
        widget=uwidgets.UnfoldAdminSelect2Widget,
    )
