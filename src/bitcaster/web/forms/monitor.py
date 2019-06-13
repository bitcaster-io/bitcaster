import logging

from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateTimeInput
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.models import Monitor

logger = logging.getLogger(__name__)


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
    start_date = forms.DateTimeField(
        required=True,
        input_formats=['%Y %b %d %H:%M'],
        widget=DateTimeInput(attrs={'autocomplete': 'off'},
                             format='%Y %b %d %H:%M'),
    )
    end_date = forms.DateTimeField(
        required=False,
        input_formats=['%Y %b %d %H:%M'],
        widget=DateTimeInput(attrs={'autocomplete': 'off'},
                             format='%Y %b %d %H:%M',),
    )

    class Meta:
        model = Monitor
        fields = ('name', 'description',
                  'start_date',
                  'end_date', 'rate', 'max_events', 'config')

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
        elif self.handler:
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
        valid = super().is_valid()
        if self.handler:
            valid = valid and self.serializer.is_valid()
            if self._errors:
                self._errors.update(self.serializer.errors)
            elif self.serializer.errors:
                self._errors = self.serializer.errors
        return valid
