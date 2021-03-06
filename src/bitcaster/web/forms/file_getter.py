import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.models import FileGetter

logger = logging.getLogger(__name__)


class FileGetterForm(forms.ModelForm):
    class Meta:
        model = FileGetter
        exclude = []
        fields = ('name', 'handler', 'config', 'description',
                  'enabled',)

    def clean_enabled(self):
        value = self.cleaned_data['enabled']
        if value:
            if not self.instance:
                raise ValidationError('FileGetter must be configured')
            elif not self.instance.is_configured:
                raise ValidationError('Configure monitor before enable it')
        return value


class FileGetterCreate1(forms.ModelForm):
    handler = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = FileGetter
        fields = ('handler',)


class FileGetterUpdateConfigurationForm(forms.ModelForm):
    config = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = FileGetter
        fields = ('name', 'description', 'config')

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.handler = kwargs.pop('handler', None)
        super().__init__(*args, **kwargs)

    @cached_property
    def serializer(self):
        args = {'application': self.application}
        if self.data:
            args['data'] = self.data
        elif self.instance:
            args['data'] = self.instance.config

        self.instance.application = self.application
        if self.instance and self.instance.handler:
            ser = self.instance.handler.get_options_form(**args)
        else:
            ser = self.handler(self.instance).get_options_form(**args)
        if args['data']:
            ser.is_valid()
        return ser

    def clean_name(self):
        name = self.cleaned_data['name']
        if not self.instance or not self.instance.pk:
            if self.application.filegetters.filter(name=name).exists():
                raise ValidationError(_('FileGetter with this name already exists'))
        return name

    def clean_config(self):
        if self.data:
            self.cleaned_data['config'] = self.serializer.data
            return self.serializer.data

    # def is_valid(self):
    #     valid = self.serializer.is_valid()
    #     valid = valid and super().is_valid()
    #     # if self.data:
    #     if self._errors:
    #         self._errors.update(self.serializer.errors)
    #     return valid
