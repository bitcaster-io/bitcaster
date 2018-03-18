# -*- coding: utf-8 -*-
import logging

from django import forms
from django.core.exceptions import ValidationError

from bitcaster.models import Channel, Message

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    channels = forms.ModelMultipleChoiceField(queryset=Channel.objects.none())

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        if self.application:
            self.fields['event'].queryset = self.application.events.all()
            self.fields['channels'].queryset = self.application.channels.all()

    def clean(self):
        event = self.cleaned_data['event']
        qs = Message.objects.filter(application=self.application, event=event)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        for channel in self.cleaned_data['channels']:
            if qs.filter(channels=channel).exists():
                raise ValidationError(f'A message for channel {channel} already exists')

    class Meta:
        model = Message
        fields = ('name', 'event', 'subject', 'body', 'channels', 'language')
