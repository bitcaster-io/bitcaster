# -*- coding: utf-8 -*-
"""
bitcaster / event
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django import forms
from django.contrib.postgres.forms import JSONField
from django.forms import Form
from jsoneditor.forms import JSONEditor
from rest_framework.exceptions import ValidationError as DRFValidationError

from bitcaster.models import Event

logger = logging.getLogger(__name__)


class EventForm(forms.ModelForm):
    arguments = JSONField(widget=JSONEditor, required=False)

    class Meta:
        model = Event
        exclude = []


class EventTriggerForm(Form):
    arguments = JSONField(widget=JSONEditor, required=False)

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def clean(self):
        expected_arguments = self.event.arguments
        arguments = self.cleaned_data['arguments']
        errors = []
        if arguments:
            for k, v in arguments.items():
                if k not in expected_arguments.keys():
                    errors.append('Invalid argument %s' % k)

        if errors:
            raise DRFValidationError({'arguments': errors})
