# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from django import forms

from bitcaster.models import ApplicationMember, OrganizationMember
from bitcaster.security import APP_ROLES

logger = logging.getLogger(__name__)


class ApplicationMemberAddForm(forms.Form):
    role = forms.TypedChoiceField(label='', choices=APP_ROLES, coerce=int)
    members = forms.ModelMultipleChoiceField(label='',
                                        queryset=OrganizationMember.objects.all())

    def __init__(self, application, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.application = application
        self.organization = application.organization
        super().__init__(*args, **kwargs)
        self.fields['members'].queryset = self.organization.memberships.all()


class ApplicationMemberForm(forms.ModelForm):
    class Meta:
        model = ApplicationMember
        fields = ('role',)

    def __init__(self, *args, **kwargs):
        form_show_labels = kwargs.pop('form_show_labels', False)
        super(ApplicationMemberForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = form_show_labels
#
#
# ApplicationMemberFormSetBase = forms.inlineformset_factory(Application,
#                                                            ApplicationMember,
#                                                            form=ApplicationMemberAddForm,
#                                                            min_num=1,
#                                                            extra=0)
#
#
# class ApplicationMemberFormSet(ApplicationMemberFormSetBase, BaseInlineFormSet):
#     def __init__(self, application, *args, **kwargs):
#         self.application = application
#         super().__init__(*args, **kwargs)
#
#     def get_form_kwargs(self, index):
#         ret = super().get_form_kwargs(index)
#         ret['application'] = self.application
#         ret['initial'] = {'role': APP_ROLES.MEMBER}
#
#         return ret
