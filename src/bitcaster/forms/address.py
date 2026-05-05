from unfold.widgets import UnfoldAdminSelectWidget

from django import forms

from bitcaster.models import Address, Channel

from .actions import GenericActionForm


class AssignToChannelForm(GenericActionForm):
    channel = forms.ModelChoiceField(queryset=Channel.objects.all(), widget=UnfoldAdminSelectWidget)


class AddressForm(forms.ModelForm["Address"]):
    class Meta:
        model = Address
        fields = ("user", "name", "type", "value")
