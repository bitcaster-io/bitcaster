import logging

from django import forms
from django.utils.translation import gettext as _

from bitcaster.models import Application

logger = logging.getLogger(__name__)


class ApplicationCreateForm(forms.ModelForm):
    # slug = forms.SlugField(validators=[ReservedWordValidator()], required=False)

    class Meta:
        model = Application
        fields = ['name', 'timezone', ]


class ApplicationForm(forms.ModelForm):
    dev_mode_message = forms.CharField(label=_('Message header when in developer mode'),
                                       widget=forms.Textarea)

    class Meta:
        model = Application
        fields = ['name', 'timezone', 'enabled']

    def get_initial_for_field(self, field, field_name):
        if field_name == 'dev_mode_message':
            return self.instance.storage.get('dev_mode_message', Application.DEF_MESSAGE)

        return super().get_initial_for_field(field, field_name)

    def save(self, commit=True):
        self.instance.storage['dev_mode_message'] = self.cleaned_data['dev_mode_message']
        self.instance.save()
        return self.instance
