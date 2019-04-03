# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from dal_select2.widgets import ModelSelect2, Select2
from django import forms
from django.forms import BaseInlineFormSet
from django.urls import reverse

from bitcaster.models import Application, ApplicationMember, OrganizationMember
from bitcaster.security import APP_ROLES

logger = logging.getLogger(__name__)


class ApplicationMemberAddForm(forms.ModelForm):
    org_member = forms.ModelChoiceField(label='',
                                        queryset=OrganizationMember.objects.all(),
                                        widget=ModelSelect2(url='app-candidate-autocomplete')
                                        )
    role = forms.ChoiceField(label='', choices=APP_ROLES,
                             widget=Select2)

    class Meta:
        model = ApplicationMember
        fields = ('org_member', 'role')

    def __init__(self, application, *args, **kwargs):
        self.application = application
        self.organization = application.organization
        super().__init__(*args, **kwargs)
        self.fields['org_member'].queryset = self.organization.memberships.all()
        self.fields['org_member'].widget.url = reverse('app-candidate-autocomplete',
                                                       args=[self.organization.slug,
                                                             self.application.slug]
                                                       )


class ApplicationMemberForm(forms.ModelForm):
    class Meta:
        model = ApplicationMember
        fields = ('role',)

    def __init__(self, *args, **kwargs):
        form_show_labels = kwargs.pop('form_show_labels', False)
        super(ApplicationMemberForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = form_show_labels


ApplicationMemberFormSetBase = forms.inlineformset_factory(Application,
                                                           ApplicationMember,
                                                           form=ApplicationMemberAddForm,
                                                           min_num=1,
                                                           extra=0)


class ApplicationMemberFormSet(ApplicationMemberFormSetBase, BaseInlineFormSet):
    def __init__(self, application, *args, **kwargs):
        self.application = application
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        ret = super().get_form_kwargs(index)
        ret['application'] = self.application
        ret['initial'] = {'role': APP_ROLES.MEMBER}

        return ret
