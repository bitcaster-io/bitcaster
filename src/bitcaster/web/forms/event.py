import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers
from strategy_field.utils import fqn

from bitcaster.models import Channel, DispatcherMetaData, Event

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
    channels = forms.ModelMultipleChoiceField(Channel.objects.none())

    class Meta:
        model = Event
        fields = ('name', 'description', 'channels', 'subscription_policy',
                  'attachment',
                  'need_confirmation',
                  'reminders',
                  'reminder_interval', 'event_expiration')

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        enabled_dispatcher = DispatcherMetaData.objects.enabled().values_list('handler',
                                                                              flat=True)
        self.fields['channels'].queryset = Channel.objects.selectable(self.application.organization,
                                                                      handler__in=enabled_dispatcher)

    def _get_validation_exclusions(self):
        exclude = super()._get_validation_exclusions()
        exclude.remove('application')
        return exclude

    def clean_name(self):
        value = self.cleaned_data['name']
        if self.instance.pk:
            qs = self.application.events.filter(name=value).exclude(id=self.instance.pk)
        else:
            qs = self.application.events.filter(name=value)

        if qs.exists():
            raise ValidationError(_('Event with this Name already exists.'))
        return value

    def full_clean(self):
        self.instance.application = self.application
        super().full_clean()

    def save(self, commit=True):
        if self.application:
            self.instance.application = self.application
        self.instance.need_confirmation = bool(self.cleaned_data['need_confirmation'])
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
