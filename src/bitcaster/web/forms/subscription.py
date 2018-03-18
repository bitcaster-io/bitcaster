# -*- coding: utf-8 -*-
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from rest_framework import serializers

from bitcaster.configurable import get_full_config
from bitcaster.models import Subscription

logger = logging.getLogger(__name__)


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        exclude = []

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        if instance and not initial:
            initial = {'config': get_full_config(instance.channel.handler.subscription_class,
                                                 instance.config)}
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)

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
