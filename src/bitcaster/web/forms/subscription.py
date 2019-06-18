import logging

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.utils.translation import gettext as _, ungettext
from rest_framework import serializers

from bitcaster.configurable import get_full_config
from bitcaster.models import (Channel, Event, Organization,
                              OrganizationMember, Subscription, User,)
from bitcaster.state import state

logger = logging.getLogger(__name__)


class EventSubscriptionCreateForm(forms.Form):
    channel = forms.ModelChoiceField(queryset=Channel.objects.none())
    members = forms.ModelMultipleChoiceField(label='',
                                             queryset=User.objects.none())
    type = forms.ChoiceField(
        choices=((Subscription.STATUSES.PENDING, _('Send only invitation. Do not actually subscribe users.')),
                 (Subscription.STATUSES.OWNED, _('Subscribe users but let them freedom to unsubscribe.')),
                 (Subscription.STATUSES.MANAGED, _('Subscribe users and lock subscription. Users cannot unsubscribe.')),
                 ))

    def __init__(self, application, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.application = application
        self.organization = application.organization
        super().__init__(*args, **kwargs)
        # if self.is_bound:
        self.fields['members'].queryset = self.organization.members.all()
        self.fields['channel'].queryset = self.instance.channels.all()

    def clean_type(self):
        value = self.cleaned_data['type']
        if value == 3:
            if self.instance.subscription_policy != Event.POLICIES.MANAGED:
                raise ValidationError(_('Event must have a MANAGED subscription policy to use this option'))
        return value

    def clean(self):
        duplicated = []
        invalid = []
        channel = self.cleaned_data['channel']
        value = self.cleaned_data['members']
        for user in value:
            if not user.has_address_for_channel(channel):
                invalid.append(user.display_name)
            elif user.subscriptions.filter(event=self.instance, channel=channel).exists():
                duplicated.append(user.display_name)

        msg = []
        if invalid:
            msg.append(ungettext('%s does not have valid address for this channel',
                                 '%s do not have valid address for this channel',
                                 len(invalid)
                                 ) % ','.join(invalid))

        if duplicated:
            msg.append(ungettext('%s is already subscribed',
                                 '%s are already subscribed',
                                 len(duplicated)
                                 ) % ','.join(duplicated))

        if msg:
            raise ValidationError(msg)

        return self.cleaned_data


class EventSubscriptionForm(forms.ModelForm):
    trigger_by = forms.ModelChoiceField(User.objects.all(),
                                        required=False)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.event = kwargs.pop('event', None)
        self.requestor = kwargs.pop('requestor', None)
        super().__init__(*args, **kwargs)
        if self.event:
            self.fields['channel'].queryset = self.event.enabled_channels.all()
        if self.instance:
            self.fields['assignment'].queryset = self.instance.subscriber.assignments.filter(
                channel=self.instance.channel)

    def clean_config(self):
        config = self.cleaned_data['config']
        if self.instance:
            handler = self.instance.channel.handler
            serializer_class = handler.subscription_class
            try:
                ser = serializer_class(data=config)
                ser.is_valid(True)
                self.cleaned_data['config'] = ser.data
            except serializers.ValidationError as e:
                config = get_full_config(serializer_class, config)
                self.cleaned_data['config'] = config
                self.instance.config = config
                raise ValidationError(str(e))

        return self.cleaned_data['config']

    def clean(self):
        cleaned_data = super().clean()
        if self.event:
            cleaned_data['event'] = self.event
        cleaned_data['trigger_by'] = state.request.user
        return cleaned_data

    class Meta:
        model = Subscription
        fields = ('subscriber', 'channel', 'event', 'trigger_by', 'assignment')


SubscriptionForm = EventSubscriptionForm


class InviteForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.event = kwargs.pop('event', None)
        self.requestor = kwargs.pop('requestor', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganizationMember
        fields = ('email',)


class InviteBaseFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.requestor = kwargs.pop('requestor')
        super().__init__(*args, **kwargs)
        self.form_kwargs['event'] = self.event
        self.form_kwargs['requestor'] = self.requestor


InviteFormSet = forms.inlineformset_factory(Organization,
                                            OrganizationMember,
                                            form=InviteForm,
                                            formset=InviteBaseFormSet,
                                            min_num=1,
                                            extra=0)
