# -*- coding: utf-8 -*-
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, BaseInlineFormSet
from rest_framework import serializers

from bitcaster.configurable import get_full_config
from bitcaster.models import (Event, Organization, OrganizationMember,
                              Subscription, User,)
from bitcaster.state import state

logger = logging.getLogger(__name__)


# class SubscriptionForm(forms.ModelForm):
#     class Meta:
#         model = Subscription
#         exclude = []
#
#     def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
#                  label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
#         if instance and not initial:
#             initial = {'config': get_full_config(instance.channel.handler.subscription_class,
#                                                  instance.config)}
#         super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
#                          use_required_attribute)
#
#     def clean_config(self):
#         config = self.cleaned_data['config']
#         if self.instance:
#             handler = self.instance.channel.handler
#             serializer_class = handler.subscription_class
#             try:
#                 ser = serializer_class(data=config)
#                 ser.is_valid(True)
#                 self.cleaned_data['config'] = ser.data
#             except serializers.ValidationError as e:
#                 config = get_full_config(serializer_class, config)
#                 self.cleaned_data['config'] = config
#                 self.instance.config = config
#                 raise ValidationError(str(e))
#
#         return self.cleaned_data['config']


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
        fields = ('subscriber', 'channel', 'event', 'trigger_by')


SubscriptionForm = EventSubscriptionForm


class SubscriptionBaseFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.requestor = kwargs.pop('requestor')
        super().__init__(*args, **kwargs)
        self.form_kwargs['event'] = self.event
        self.form_kwargs['requestor'] = self.requestor


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


SubscriptionFormSet = forms.inlineformset_factory(Event,
                                                  Subscription,
                                                  form=EventSubscriptionForm,
                                                  formset=SubscriptionBaseFormSet,
                                                  min_num=1,
                                                  extra=0)
InviteFormSet = forms.inlineformset_factory(Organization,
                                            OrganizationMember,
                                            form=InviteForm,
                                            formset=InviteBaseFormSet,
                                            min_num=1,
                                            extra=0)
