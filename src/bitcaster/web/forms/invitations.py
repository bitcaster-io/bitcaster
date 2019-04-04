import logging

from crispy_forms.helper import FormHelper
from django import forms
from django.forms import BaseInlineFormSet

from bitcaster.models import Application, Organization
from bitcaster.models.invitation import Invitation

logger = logging.getLogger(__name__)


class ApplicationInvitationForm(forms.ModelForm):
    target = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = Invitation
        fields = ('target', 'team')

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


class OrganizationInvitationForm(forms.ModelForm):
    target = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = Invitation
        fields = ('target', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


OrganizationInvitationFormSet = forms.inlineformset_factory(Organization,
                                                            Invitation,
                                                            form=OrganizationInvitationForm,
                                                            formset=BaseInlineFormSet,
                                                            min_num=1,
                                                            extra=0)
