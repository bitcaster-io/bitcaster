# -*- coding: utf-8 -*-
import logging

from django import forms
from django.contrib.postgres.forms import JSONField
# from django.forms import Form, formset_factory, ModelForm
from django.core.exceptions import ValidationError
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


class ArgumentLineForm(forms.Form):
    name = forms.CharField()
    type = forms.ChoiceField(choices=FIELD_TYPES)


class EventForm(forms.ModelForm):
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs={'rows': '2'}))

    class Meta:
        model = Event
        fields = ('name', 'description', 'channels', 'subscription_policy')

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)

    def _get_validation_exclusions(self):
        exclude = super()._get_validation_exclusions()
        exclude.remove('application')
        return exclude

    def clean_name(self):
        value = self.cleaned_data['name']
        if self.application.events.filter(name=value).exists():
            raise ValidationError('Event with this Name already exists.')

    def full_clean(self):
        self.instance.application = self.application
        super().full_clean()

    def save(self, commit=True):
        if self.application:
            self.instance.application = self.application
        return super().save(commit)


class EventCreateSelectChannel(forms.Form):
    channels = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)
        self.fields['channels'].queryset = self.application.channels.all()


class EventCreateMessageForm(forms.Form):
    subject = forms.CharField(max_length=200, required=False)
    body = forms.CharField(widget=forms.Textarea())
    channel = forms.CharField(disabled=True)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)


class EventCreateSetupMessage(forms.Form):
    subject = forms.CharField(max_length=200, required=False)
    body = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.channels = kwargs.pop('channels', [])
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)
        self.formset_class = forms.formset_factory(EventCreateMessageForm,
                                                   extra=0)
        # initial = []
        # for c in self.channels:
        #     initial.append({'channel': c})
        # self.msgForms = self.formset_class(initial=initial)


class EventTriggerForm(forms.Form):
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


# create wizard
class EventCreateConfig(forms.Form):
    pass
