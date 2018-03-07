# -*- coding: utf-8 -*-
"""
mercury / message
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django import forms

from mercury.models import Event

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = []
