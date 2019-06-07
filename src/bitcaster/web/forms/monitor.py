import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.models import Monitor

logger = logging.getLogger(__name__)


class MonitorForm(forms.ModelForm):
    class Meta:
        model = Monitor
        exclude = []
        fields = ('name', 'handler', 'config', 'description',
                  'enabled',)

    def __init__(self, *args, **kwargs):
        self.serializer_class = kwargs.pop('serializer', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.handler:
            self.serializer_class = self.instance.handler.options_class

    def clean_enabled(self):
        value = self.cleaned_data['enabled']
        if value:
            if not self.instance:
                raise ValidationError('Monitor must be configured')
            elif not self.instance.is_configured:
                raise ValidationError('Configure monitor before enable it')
        return value

    def is_valid(self):
        valid = super().is_valid()
        if self.serializer_class:
            valid = valid and self.serializer.is_valid()
        return valid


class MonitorCreate1(forms.ModelForm):
    handler = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Monitor
        fields = ('handler',)


class MonitorUpdateConfigurationForm(forms.ModelForm):
    config = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Monitor
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
            if self.application.monitors.filter(name=name).exists():
                raise ValidationError(_('Monitor with this name already exists'))
        return name

    def clean_config(self):
        if self.data:
            self.cleaned_data['config'] = self.serializer.data
            return self.serializer.data

    def is_valid(self):
        valid = self.serializer.is_valid()
        valid = valid and super().is_valid()
        if self._errors:
            self._errors.update(self.serializer.errors)
        elif self.serializer.errors:
            self._errors = self.serializer.errors
        return valid
