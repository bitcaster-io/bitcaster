from django import forms
from django.utils.translation import gettext_lazy as _
from unfold import widgets as uwidgets

from ..models import DistributionList
from .actions import GenericActionForm


class SelectDistributionForm(GenericActionForm):
    dl = forms.ModelChoiceField(
        label=_("Distribution List"),
        queryset=DistributionList.objects.all(),
        required=True,
        blank=False,
        widget=uwidgets.UnfoldAdminSelectWidget,
    )
