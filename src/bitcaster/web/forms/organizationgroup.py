# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import OrganizationGroup

logger = logging.getLogger(__name__)


class OrganizationGroupAddMemberForm(forms.Form):
    user = forms.IntegerField()


class OrganizationGroupForm(forms.ModelForm):
    # applications = forms.ModelMultipleChoiceField(queryset=Application.objects.all(),
    #                                               required=False,
    #                                               widget=ModelSelect2Multiple(url='application-autocomplete')
    #                                               )
    # members = forms.ModelMultipleChoiceField(queryset=OrganizationMember.objects.all(),
    #                                          required=False,
    #                                          widget=ModelSelect2Multiple(url='org-member-autocomplete')
    #                                          )

    class Meta:
        model = OrganizationGroup
        fields = ('name', 'closed')

    # def __init__(self, organization, *args, **kwargs):
    #     self.organization = organization
    #     form_show_labels = kwargs.pop('form_show_labels', True)
    #     super().__init__(*args, **kwargs)
    #     self.fields['applications'].queryset = self.organization.applications.all()
    #     self.fields['applications'].widget.url = reverse('application-autocomplete',
    #                                                      args=[self.organization.slug]
    #                                                      )
    #
    #     self.fields['members'].queryset = self.organization.members.all()
    #     self.fields['members'].widget.url = reverse('org-member-autocomplete',
    #                                                 args=[self.organization.slug]
    #                                                 )
    #
    #     self.helper = FormHelper()
    #     self.helper.form_show_labels = form_show_labels
