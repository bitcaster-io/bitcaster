from django import forms

from bitcaster.models import Address, Channel


class UserAddressForm(forms.ModelForm):
    label = forms.CharField()
    address = forms.CharField()
    channels = forms.ModelMultipleChoiceField(queryset=Channel.objects.none())

    class Meta:
        model = Address
        fields = ('label', 'address', 'channels')

    def __init__(self, *args, **kwargs):
        # self.address = instance
        # self.user = user
        super().__init__(*args, **kwargs)
        self.fields['channels'].queryset = Channel.objects.valid()
