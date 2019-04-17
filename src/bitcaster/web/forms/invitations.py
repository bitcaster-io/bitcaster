# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext as _

from bitcaster.models import Application, OrganizationGroup
from bitcaster.models.invitation import Invitation

logger = logging.getLogger(__name__)


class ApplicationInvitationForm(forms.ModelForm):
    target = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = Invitation
        fields = ('target', 'teams')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


ApplicationInvitationFormSet = forms.inlineformset_factory(Application,
                                                           Invitation,
                                                           form=ApplicationInvitationForm,
                                                           formset=BaseInlineFormSet,
                                                           min_num=1,
                                                           extra=0)
#
#
# class OrganizationInvitationForm(forms.ModelForm):
#     target = forms.EmailField(required=True,
#                               widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
#
#     class Meta:
#         model = Invitation
#         fields = ('target', 'role')
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_show_labels = False


# OrganizationInvitationFormSet = forms.inlineformset_factory(Organization,
#                                                             Invitation,
#                                                             form=OrganizationInvitationForm,
#                                                             formset=BaseInlineFormSet,
#                                                             min_num=1,
#                                                             extra=0)
#

class OrganizationInvitationForm(forms.Form):
    emails = forms.CharField()
    role = forms.IntegerField()
    groups = forms.ModelMultipleChoiceField(queryset=OrganizationGroup.objects.none(),
                                            required=False)

    def __init__(self, **kwargs):
        self.organization = kwargs.pop('organization')
        super().__init__(**kwargs)
        self.fields['groups'].queryset = self.organization.groups.all()

    def clean_emails(self):
        raw_value = self.cleaned_data['emails']
        emails = list(map(lambda s: s.strip(), raw_value.split(',')))
        validator = EmailValidator('one or more entries are not valid')
        for email in emails:
            try:
                validator(email)
            except ValidationError:
                raise ValidationError(_('%(email)s is not a valid email address') % dict(email=email))
        return emails
#             212-326-7123
