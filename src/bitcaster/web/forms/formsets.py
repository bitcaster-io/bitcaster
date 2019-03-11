# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from bitcaster.models import Organization, OrganizationMember

logger = logging.getLogger(__name__)


class OrganizationInvitationFormSet(BaseInlineFormSet):
    pass


class OrganizationInvitationForm(forms.ModelForm):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = OrganizationMember
        fields = ('email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    def clean_email(self):
        if self.cleaned_data['email'] == self.instance.organization.owner.email:
            raise ValidationError('This email is from the Organization owner')
        return self.cleaned_data['email']


OrganizationInvitationFormSet = forms.inlineformset_factory(Organization,
                                                            OrganizationMember,
                                                            form=OrganizationInvitationForm,
                                                            formset=OrganizationInvitationFormSet,
                                                            min_num=1,
                                                            extra=0)
