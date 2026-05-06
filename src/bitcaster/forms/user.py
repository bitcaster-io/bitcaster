from unfold import widgets as uwidgets

from django import forms
from django.utils.translation import gettext_lazy as _

from .actions import GenericActionForm
from ..models import DistributionList


class SelectDistributionForm(GenericActionForm):
    dl = forms.ModelChoiceField(
        label=_("Distribution List"),
        queryset=DistributionList.objects.all(),
        required=True,
        blank=False,
        widget=uwidgets.UnfoldAdminSelectWidget,
    )
