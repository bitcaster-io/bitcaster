# -*- coding: utf-8 -*-
"""
mercury / application
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django import forms

from mercury.db.validators import ReservedWordValidator
from mercury.models import Application

logger = logging.getLogger(__name__)


class ApplicationCreateForm(forms.ModelForm):
    slug = forms.SlugField(validators=[ReservedWordValidator()], required=False)

    class Meta:
        model = Application
        fields = ['name', 'timezone', 'allowed_origins', 'slug']


class ApplicationForm(forms.ModelForm):
    # flags = BitFormField(initial=0)

    class Meta:
        model = Application
        exclude = ['flags', 'teams']
