from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from bitcaster.models import ApplicationTriggerKey, Event


class ApplicationTriggerKeyForm(forms.ModelForm):
    events = forms.ModelMultipleChoiceField(
        label=_('allowed events'),
        queryset=Event.objects.none(),
        required=False)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super().__init__(*args, **kwargs)
        if self.application:
            self.fields['events'].queryset = Event.objects.filter(application=self.application)

    def save(self, commit=True):
        if self.application:
            self.instance.application = self.application

        return super().save(commit)

    def clean_name(self):
        value = self.cleaned_data['name']
        if self.application.events.filter(name=value).exists():
            raise ValidationError('Key with this Name already exists.')
        return value

    class Meta:
        model = ApplicationTriggerKey
        fields = ('name', 'enabled', 'events', 'all_events')
