# -*- coding: utf-8 -*-
"""
mercury / channel
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django import forms
from django.core.exceptions import ValidationError

from mercury.models import Channel

logger = logging.getLogger(__name__)


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        exclude = []
        fields = ('name', 'application', 'handler', 'config', 'description',
                  'enabled', 'deprecated')

    def clean_enabled(self):
        value = self.cleaned_data['enabled']
        if value:
            if not self.instance:
                raise ValidationError("Channel must be configured")
            elif not self.instance.is_configured:
                raise ValidationError("Configure channel before enable it")
        return value
