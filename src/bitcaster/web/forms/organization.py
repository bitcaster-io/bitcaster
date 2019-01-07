# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Organization
from bitcaster.web.forms.fields import EmailField

logger = logging.getLogger(__name__)


class OrganizationSystemForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("name", 'admin_email', 'slug', 'avatar',
                  'default_role', 'rate_limit')


class OrganizationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'organization'}))
    admin_email = EmailField()

    class Meta:
        model = Organization
        fields = ("name", 'admin_email', 'slug', 'avatar')

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        if not self.instance or self.instance.is_core:
            self.fields['slug'].disabled = True
            self.fields['slug'].validators = []

    def clean_slug(self):
        value = self.cleaned_data['slug']
        if self.instance and self.instance.is_core:
            return self.instance.slug
        return value
