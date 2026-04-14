from typing import Any

from django import forms

from bitcaster.forms import unfold
from bitcaster.models import Address, Assignment


class AssignmentForm(forms.ModelForm["Assignment"]):
    class Meta:
        model = Assignment
        fields = ("address", "channel", "validated", "active")


class AssignmentInlineForm(forms.ModelForm["Assignment"]):
    address = forms.ModelChoiceField(queryset=Address.objects.none(), widget=unfold.UnfoldAdminSelectWidget)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user.pk:
            self.fields["address"].queryset = self.user.addresses.all()
            self.fields["address"].widget.queryset = self.user.addresses.all()

    class Meta:
        model = Assignment
        fields = (
            "address",
            "channel",
        )


class DistributionListInlineForm(forms.ModelForm["Assignment"]):
    address = forms.ModelChoiceField(queryset=Address.objects.none(), widget=unfold.UnfoldAdminSelectWidget)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user.pk:
            self.fields["address"].queryset = self.user.addresses.all()
            self.fields["address"].widget.queryset = self.user.addresses.all()

    class Meta:
        model = Assignment
        fields = (
            "address",
            "channel",
        )
