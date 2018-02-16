# -*- coding: utf-8 -*-

import json
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (UserChangeForm as _UserChangeForm,
                                       UserCreationForm as _UserCreationForm,
                                       UsernameField,)
from django.contrib.postgres.forms import JSONField
from django.core.exceptions import ValidationError as DjangoValidationError
from django.forms import Form
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# from bitfield.forms import BitFormField
from jsoneditor.forms import JSONEditor
from rest_framework.exceptions import ValidationError

from mercury import logging
from mercury.models import Application, Channel, Event, Subscription, User
from mercury.utils import import_by_name
from mercury.utils.language import flatten

logger = logging.getLogger(__name__)


class UserChangeForm(_UserChangeForm):
    last_password_change = forms.DateTimeField(disabled=True, required=False)
    date_joined = forms.DateTimeField(disabled=True, required=False)
    last_login = forms.DateTimeField(disabled=True, required=False)

    class Meta:
        model = User
        exclude = ('user_permissions', 'groups')
        field_classes = {'username': UsernameField}


class UserCreationForm(_UserCreationForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    email = forms.EmailField()
    password1 = forms.CharField(
        label=_("Password"),
        required=False,
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        required=False,
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ("username", 'email', 'timezone', 'language', 'country')
        field_classes = {'username': UsernameField}

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        else:
            user.set_unusable_password()

        if commit:
            user.save()
        return user


class ApplicationForm(forms.ModelForm):
    # flags = BitFormField(initial=0)

    class Meta:
        model = Application
        exclude = ['flags']


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
            valid, errors = handler.validate_configuration(config, False)
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
    class Meta:
        model = Channel
        exclude = []
        fields = ('name', 'application', 'handler', 'config', 'description',
                  'enabled', 'deprecated')


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        exclude = []


class EventTriggerForm(Form):
    arguments = JSONField(widget=JSONEditor, required=False)

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def clean(self):
        expected_arguments = self.event.arguments
        arguments = self.cleaned_data['arguments']
        errors = []
        if arguments:
            for k, v in arguments.items():
                if k not in expected_arguments.keys():
                    errors.append('Invalid argument %s' % k)

        if errors:
            raise ValidationError({'arguments': errors})
