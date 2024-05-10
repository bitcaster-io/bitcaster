from django import forms

from bitcaster.models import Validation


class ValidationForm(forms.ModelForm["Validation"]):
    # address = forms.ModelChoiceField(
    #     queryset=Address.objects.exclude(name=Bitcaster.PROJECT),
    #     required=True,
    #     widget=AutocompletSelectEnh(Validation._meta.get_field("address"), admin.site),
    # )
    # channel = forms.ModelChoiceField(
    #     queryset=Channel.objects.exclude(name=Bitcaster.PROJECT),
    #     required=True,
    #     widget=AutocompletSelectEnh(Validation._meta.get_field("channel"), admin.site),
    # )

    class Meta:
        model = Validation
        fields = ("address", "channel", "validated", "active")
