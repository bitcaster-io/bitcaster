# -*- coding: utf-8 -*-
import logging

from crispy_forms import helper
from django import forms
from django.core.exceptions import ValidationError

from bitcaster.models import ApplicationRole

logger = logging.getLogger(__name__)


class ApplicationRoleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper(self)

    class Meta:
        fields = ('role', 'team')
        model = ApplicationRole

    def validate_unique(self):
        self.instance.application = self.application
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            self._update_errors(e)

    def save(self, commit=True):
        if self.application:
            self.instance.application = self.application
        return super().save(commit)
