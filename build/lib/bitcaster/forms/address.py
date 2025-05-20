from django import forms
from django.contrib import admin

from bitcaster.models import Address, User

from .widgets import AutocompletSelectEnh


class AddressForm(forms.ModelForm["Address"]):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=AutocompletSelectEnh(Address._meta.get_field("user"), admin.site),
    )

    class Meta:
        model = Address
        fields = "__all__"
