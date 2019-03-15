# -*- coding: utf-8 -*-
import logging

from crispy_forms import helper, layout
from crispy_forms.bootstrap import FormActions
from django import forms
from django.utils.translation import gettext as _

from bitcaster.models import Team

logger = logging.getLogger(__name__)


class TeamForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper(self)
        self.helper.layout = helper.Layout(*self.Meta.fields,
                                           FormActions(
                                               layout.Submit('submit', _('Save'), css_class='btn-primary')
                                           )
                                           )

    class Meta:
        fields = ('name', 'manager', 'description', 'members')
        model = Team
