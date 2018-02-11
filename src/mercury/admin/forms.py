# -*- coding: utf-8 -*-

import json
from django import forms
from django.contrib.postgres.forms import JSONField
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.safestring import mark_safe

from bitfield.forms import BitFormField
from jsoneditor.forms import JSONEditor
from rest_framework.exceptions import ValidationError

from mercury import logging
from mercury.models import Application, Channel, Event, Subscription
from mercury.utils import import_by_name
from mercury.utils.language import flatten

logger = logging.getLogger(__name__)


class ApplicationForm(forms.ModelForm):
    flags = BitFormField(initial=0)

    class Meta:
        model = Application
        exclude = []


class EventForm(forms.ModelForm):
    arguments = JSONField(widget=JSONEditor, required=False)

    class Meta:
        model = Event
        exclude = []


class MessageForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = []


class ValidateJsonMixin(object):
    def clean(self):
        handler_class = self.cleaned_data.get('handler', None)
        config = self.cleaned_data.get('config', {})
        enabled = self.cleaned_data.get('enabled', False)

        if handler_class and enabled:
            try:
                handler = import_by_name(handler_class)
            except ValidationError as e:
                raise DjangoValidationError(e)
            if not config:
                config = handler.defaults()
            else:
                config = {**handler.defaults(), **config}
            valid, errors = handler.validate(config, False)
            # Ugly but it is the only way
            d = self.data.copy()
            d['config'] = json.dumps(config)
            self.data = d
            if not valid:
                ret = []
                for k, v in errors.items():
                    ret.append("<b>{0}</b>:{1} ".format(k, ",".join(flatten(v))))
                raise DjangoValidationError({'config': mark_safe(" ".join(flatten(ret)))})

        return super().clean()


class DispatcherConfigForm(ValidateJsonMixin, forms.ModelForm):
    # handler = StrategyFormField(registry=dispatcher_registry)
    class Meta:
        model = Channel
        exclude = []
        fields = ('name', 'application', 'handler', 'config', 'description',
                  'enabled', 'deprecated')
    #
    # def clean(self):
    #     ret = super().clean()
    #     enabled = self.cleaned_data['enabled']
    #     if enabled:
    #         handler = self.cleaned_data['handler']
    #         config = self.cleaned_data['config']
    #         try:
    #             handler.validate(config, True)
    #         except Exception as e:
    #             raise ValidationError(e)
    #     return ret


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        exclude = []
