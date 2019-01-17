from django import forms

from bitcaster.models import ApplicationTriggerKey, Event


class ApplicationTriggerKeyForm(forms.ModelForm):
    events = forms.ModelMultipleChoiceField(queryset=Event.objects.none(),
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

    class Meta:
        model = ApplicationTriggerKey
        fields = ('name', 'enabled', 'events', 'all_events')
