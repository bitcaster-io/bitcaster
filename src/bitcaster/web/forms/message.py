# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Channel, Message

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput)
    channel = forms.ModelChoiceField(queryset=Channel.objects.none(),
                                     widget=forms.HiddenInput)
    enabled = forms.BooleanField(required=False)

    event = None

    class Meta:
        model = Message
        fields = ('name', 'subject', 'body', 'channel', 'id', 'enabled')

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        if self.event:
            self.fields['channel'].queryset = self.event.channels.all()
