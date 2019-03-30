# -*- coding: utf-8 -*-
import logging

from crispy_forms import helper, layout
from crispy_forms.bootstrap import FormActions
from dal_select2.widgets import ModelSelect2, ModelSelect2Multiple
from django import forms
from django.utils.translation import gettext as _

from bitcaster.models import OrganizationMember, Team, User
from bitcaster.security import ROLES

logger = logging.getLogger(__name__)


class TeamForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(queryset=OrganizationMember.objects.all(),
                                             widget=ModelSelect2Multiple(url='user-autocomplete')
                                             )

    manager = forms.ModelChoiceField(queryset=User.objects.all(),
                                     widget=ModelSelect2(url='user-autocomplete')
                                     )
    role = forms.ChoiceField(choices=ROLES,
                             widget=ModelSelect2())

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application')
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper(self)
        self.helper.layout = helper.Layout(*self.Meta.fields,
                                           FormActions(
                                               layout.Submit('submit', _('Save'), css_class='btn-primary')
                                           ))
        self.fields['manager'].queryset = User.objects.filter(memberships__organization=self.application.organization)

    class Meta:
        fields = ('name', 'manager', 'description', 'role', 'members')
        model = Team
