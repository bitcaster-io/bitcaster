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
from django.forms import Form, formset_factory
from jsoneditor.forms import JSONEditor
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from strategy_field.utils import fqn

from bitcaster.models import Event

logger = logging.getLogger(__name__)

FIELD_TYPES = ((fqn(serializers.CharField), 'text'),
               (fqn(serializers.IntegerField), 'number'),
               (fqn(serializers.DateField), 'date'),
               )


class ArgumentLineForm(Form):
    name = forms.CharField()
    type = forms.ChoiceField(choices=FIELD_TYPES)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.arg_formset_class = formset_factory(ArgumentLineForm,
                                                 extra=0)

        super().__init__(*args, **kwargs)
        if self.instance and self.instance.arguments:
            fields_def = self.instance.arguments['fields']
            self.arguments = self.arg_formset_class(initial=fields_def)
        elif self.data:
            self.arguments = self.arg_formset_class(data=self.data)
        else:
            self.arguments = self.arg_formset_class()

    def full_clean(self):
        super().full_clean()

    def is_valid(self):
        self.arguments = self.arg_formset_class(data=self.data)
        return super().is_valid() and self.arguments.is_valid()

    def save(self, commit=True):
        if self.application:
            self.instance.application = self.application
        arguments = {"fields": []}
        for form in self.arguments:
            if form.cleaned_data:
                arguments['fields'].append({"name": form.cleaned_data["name"],
                                            "type": form.cleaned_data["type"],
                                            })
        self.instance.arguments = arguments
        return super().save(commit)


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
