import logging

from django import forms
from django.utils.functional import cached_property

from bitcaster.models import Channel

logger = logging.getLogger(__name__)


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        exclude = []
        fields = ('name', 'application', 'handler', 'config', 'description',
                  'enabled', 'deprecated')


class ChannelUpdateConfigurationForm(forms.ModelForm):
    config = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Channel
        fields = ('name', 'description', 'dispatch_page_size',
                  'dispatch_rate',
                  'config')

    def __init__(self, *args, **kwargs):
        self.serializer_class = kwargs.pop('serializer', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.handler:
            self.serializer_class = self.instance.handler.options_class

    @cached_property
    def serializer(self):
        args = {}
        if self.data:
            args = {'data': self.data}
            ser = self.serializer_class(**args)
            ser.is_valid()
        elif self.instance.pk:
            # get_full_config is required for updates
            args = {'instance': self.instance.handler.get_full_config(self.instance.config)}
            ser = self.serializer_class(**args)
        else:
            args = {'initial': self.initial}
            ser = self.serializer_class(**args)

        return ser

    def clean_config(self):
        self.cleaned_data['config'] = self.serializer.data
        return self.serializer.data

    def is_valid(self):
        valid = super().is_valid()
        if self.serializer_class:
            valid = valid and self.serializer.is_valid()
        return valid
