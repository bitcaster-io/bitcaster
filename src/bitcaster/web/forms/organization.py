# -*- coding: utf-8 -*-
"""
bitcaster / organization
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django import forms

from bitcaster.models import Organization

logger = logging.getLogger(__name__)


class OrganizationForm(forms.ModelForm):
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

    class Meta:
        model = Organization
        fields = ("name", 'billing_email', 'slug', 'avatar')
