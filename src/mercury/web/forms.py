# -*- coding: utf-8 -*-
"""
mercury / forms
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import json

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (UserChangeForm as _UserChangeForm,
                                       UserCreationForm as _UserCreationForm)
from django.contrib.auth.hashers import make_password
from django.contrib.postgres.forms import JSONField
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import Form, PasswordInput
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from jsoneditor.forms import JSONEditor
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from mercury.configurable import get_full_config
from mercury.models import Application, Channel, Event, Subscription, User
from mercury.models.organizationmember import OrganizationRole
from mercury.utils import import_by_name
from mercury.utils.language import flatten

from mercury.models import Organization


class RegistrationForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=PasswordInput)
    organization = forms.CharField(help_text="If you're signing up for a personal account, try using your own name.")
    billing_email = forms.EmailField(required=False,
        help_text="If provided, we will send all billing-related notifications to this address.")
    terms = forms.BooleanField()
    captcha = ReCaptchaField(widget=ReCaptchaWidget())

    def clean_email(self):
        value = (self.cleaned_data.get('email') or '').strip()
        if not value:
            return
        if User.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError(_('An account is already registered with that email address.'))
        return value.lower()

    def clean_organization(self):
        value = (self.cleaned_data.get('organization') or '').strip()
        if not value:
            return
        if Organization.objects.filter(name__iexact=value).exists():
            raise forms.ValidationError(_('This Organization name is already used.'))
        return value.lower()

    @transaction.atomic()
    def save(self, commit=True):
        u = User.objects.create(email=self.cleaned_data['email'],
                                name=self.cleaned_data['name'],
                                password=make_password(self.cleaned_data['password']),
                                )
        org = Organization.objects.create(name=self.cleaned_data['organization'],
                                    billing_email=self.cleaned_data['billing_email'],
                                    owner=u
                                    )
        org.add_member(u, OrganizationRole.OWNER)
        return org


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("name", 'slug', 'billing_email')


class UserChangeForm(forms.ModelForm):
    last_password_change = forms.DateTimeField(disabled=True, required=False)
    date_joined = forms.DateTimeField(disabled=True, required=False)
    last_login = forms.DateTimeField(disabled=True, required=False)

    class Meta:
        model = User
        exclude = ('user_permissions', 'groups')


class UserProfileForm(forms.ModelForm):
    friendly_name = forms.CharField(required=False)
    email = forms.EmailField(disabled=True)

    class Meta:
        model = User
        fields = ('friendly_name', 'email', 'timezone', 'language', 'country')


class UserCreationForm(_UserCreationForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

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
        fields = ('friendly_name', 'email', 'timezone', 'language', 'country')

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
            except DRFValidationError as e:
                raise ValidationError(e)
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
                raise ValidationError({'config': mark_safe(" ".join(flatten(ret)))})

        return super().clean()


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        exclude = []
        fields = ('name', 'application', 'handler', 'config', 'description',
                  'enabled', 'deprecated')

    def clean_enabled(self):
        value = self.cleaned_data['enabled']
        if value:
            if not self.instance:
                raise ValidationError("Channel must be configured")
            elif not self.instance.is_configured:
                raise ValidationError("Configure channel before enable it")
        return value


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
            raise DRFValidationError({'arguments': errors})
