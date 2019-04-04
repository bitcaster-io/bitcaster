import logging

from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout
from django import forms

from bitcaster.models import OrganizationMember

logger = logging.getLogger(__name__)


class OrganizationMemberForm(forms.ModelForm):
    class Meta:
        model = OrganizationMember
        exclude = ('organization', 'date_enrolled', 'user')

    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        form_show_labels = kwargs.pop('form_show_labels', False)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = form_show_labels

        self.helper.layout = Layout('role',
                                    HTML('{{user.email}}'),
                                    UneditableField('user', readonly=True), )
