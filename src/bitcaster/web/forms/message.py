# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Message, Channel

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    channels = forms.ModelMultipleChoiceField(queryset=Channel.objects.none())

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        if self.application:
            self.fields['event'].queryset = self.application.events.all()
            self.fields['channels'].queryset = self.application.channels.all()

    class Meta:
        model = Message
        fields = ('name', 'event', 'subject', 'body', 'channels', 'language')
