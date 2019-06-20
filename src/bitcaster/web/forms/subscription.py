import logging

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.utils.translation import gettext as _, ungettext

from bitcaster.models import (Channel, Event, Organization,
                              OrganizationMember, Subscription, User,)

logger = logging.getLogger(__name__)


class EventSubscriptionCreateForm(forms.Form):
    channel = forms.ModelChoiceField(queryset=Channel.objects.none())
    members = forms.ModelMultipleChoiceField(label='',
                                             queryset=User.objects.none())
    type = forms.ChoiceField(
        choices=(
            # (Subscription.STATUSES.PENDING, _('Send only invitation. Do not actually subscribe users.')),
            (Subscription.STATUSES.OWNED, _('Subscribe users. Let them freedom to unsubscribe.')),
            (Subscription.STATUSES.MANAGED, _('Subscribe users. Lock subscription so users cannot unsubscribe.')),
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


class EventSubscriptionEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignment'].queryset = self.instance.subscriber.assignments.filter(
            channel=self.instance.channel)

    class Meta:
        model = Subscription
        fields = ('status', 'assignment')


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
