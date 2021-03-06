import logging

from crispy_forms.helper import FormHelper
from django import forms

from bitcaster.models import Organization
from bitcaster.web.forms.fields import EmailField

logger = logging.getLogger(__name__)


class OrganizationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'organization'}))
    admin_email = EmailField()

    class Meta:
        model = Organization
        fields = ('name', 'admin_email', 'slug')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance or self.instance.is_core:
            self.fields['slug'].disabled = True
            self.fields['slug'].validators = []

    def clean_slug(self):
        value = self.cleaned_data['slug']
        if self.instance and self.instance.is_core:
            return self.instance.slug
        return value


class OrganizationOptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
