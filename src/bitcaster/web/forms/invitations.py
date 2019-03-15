# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from django import forms
from django.forms import BaseInlineFormSet

from bitcaster.models import Application, Organization
from bitcaster.models.invitation import Invitation

logger = logging.getLogger(__name__)


class InvitationForm(forms.ModelForm):
    target = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = Invitation
        fields = ('target', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    def clean_target(self):
        # if self.cleaned_data['email'] == self.instance.organization.owner.email:
        #     raise ValidationError('This email is from the Organization owner')
        return self.cleaned_data['target']


OrganizationInvitationFormSet = forms.inlineformset_factory(Organization,
                                                            Invitation,
                                                            form=InvitationForm,
                                                            formset=BaseInlineFormSet,
                                                            min_num=1,
                                                            extra=0)

ApplicationInvitationFormSet = forms.inlineformset_factory(Application,
                                                           Invitation,
                                                           form=InvitationForm,
                                                           formset=BaseInlineFormSet,
                                                           min_num=1,
                                                           extra=0)
