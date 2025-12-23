from django import forms

from bitcaster.models import Address


class AddressForm(forms.ModelForm["Address"]):
    class Meta:
        model = Address
        fields = ("user", "name", "type", "value")
