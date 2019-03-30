# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Application

logger = logging.getLogger(__name__)


class ApplicationCreateForm(forms.ModelForm):
    # slug = forms.SlugField(validators=[ReservedWordValidator()], required=False)

    class Meta:
        model = Application
        fields = ['name', 'timezone', ]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'timezone', 'enabled']
