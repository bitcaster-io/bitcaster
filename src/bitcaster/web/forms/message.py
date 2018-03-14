# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Message

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Message
        fields = ('name', 'event', 'subject', 'body')
