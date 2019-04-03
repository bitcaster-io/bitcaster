# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from dal_select2.widgets import ModelSelect2Multiple
from django import forms
from django.urls import reverse

from bitcaster.models import Application, OrganizationGroup, OrganizationMember

logger = logging.getLogger(__name__)


class OrganizationGroupForm(forms.ModelForm):
    applications = forms.ModelMultipleChoiceField(queryset=Application.objects.all(),
                                                  required=False,
                                                  widget=ModelSelect2Multiple(url='application-autocomplete')
                                                  )
    members = forms.ModelMultipleChoiceField(queryset=OrganizationMember.objects.all(),
                                             required=False,
                                             widget=ModelSelect2Multiple(url='members-autocomplete')
                                             )

    class Meta:
        model = OrganizationGroup
        fields = ('name', 'members')

    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        form_show_labels = kwargs.pop('form_show_labels', True)
        super().__init__(*args, **kwargs)
        self.fields['applications'].queryset = self.organization.applications.all()
        self.fields['applications'].widget.url = reverse('application-autocomplete',
                                                         args=[self.organization.slug]
                                                         )

        self.fields['members'].queryset = self.organization.members.all()
        self.fields['members'].widget.url = reverse('members-autocomplete',
                                                    args=[self.organization.slug]
                                                    )

        self.helper = FormHelper()
        self.helper.form_show_labels = form_show_labels
