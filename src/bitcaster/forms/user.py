from django import forms
from django.utils.translation import gettext as _

from bitcaster.models import DistributionList


class GenericActionForm(forms.Form):
    _selected_action = forms.CharField(label="", widget=forms.MultipleHiddenInput)
    select_across = forms.BooleanField(
        label="",
        required=False,
        initial=0,
        widget=forms.HiddenInput({"class": "select-across"}),
    )
    action = forms.CharField(label="", required=True, initial="", widget=forms.HiddenInput())


class SelectDistributionForm(GenericActionForm):
    dl = forms.ModelChoiceField(
        label=_("Distribution List"), queryset=DistributionList.objects.all(), required=True, blank=False
    )
