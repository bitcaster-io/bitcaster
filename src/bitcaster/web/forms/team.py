# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Team

logger = logging.getLogger(__name__)


class TeamForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization')
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ('name', 'manager', 'members')
        model = Team
