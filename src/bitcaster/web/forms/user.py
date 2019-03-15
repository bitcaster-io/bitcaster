# -*- coding: utf-8 -*-
import logging

from constance import config
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
    UserCreationForm as _UserCreationForm,)
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms import BaseInlineFormSet, PasswordInput
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError as DRFValidationError

from bitcaster.agents import serializers
from bitcaster.configurable import get_full_config
from bitcaster.db.fields import Role
from bitcaster.mail import send_mail_by_template
from bitcaster.models import Address, AddressAssignment, Subscription, User
from bitcaster.otp import totp
from bitcaster.state import state
from bitcaster.utils.email_verification import get_new_email_request
from bitcaster.utils.http import absolute_uri

logger = logging.getLogger(__name__)


class AuthenticationForm(_AuthenticationForm):
    # username = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    username = forms.CharField()
    password = forms.CharField(widget=PasswordInput(attrs={'autocomplete': 'current-password'}))


# class UserChangeForm(_UserChangeForm):
#     last_password_change = forms.DateTimeField(disabled=True, required=False)
#     date_joined = forms.DateTimeField(disabled=True, required=False)
#     last_login = forms.DateTimeField(disabled=True, required=False)
#
#     class Meta:
#         model = User
#         exclude = ('user_permissions', 'groups')


class UserInviteRegistrationForm(forms.ModelForm):
    email = forms.EmailField(disabled=True)

    class Meta:
        model = User
        fields = ('friendly_name', 'email', 'password')


def send_address_verification_email(user):
    code = totp.now()
    url = reverse('confirm-address', args=[user.pk, user.email, code])

    send_mail_by_template('[Bitcaster] Verify email address',
                          'confirm_email',
                          {'user': user,
                           'url': absolute_uri(url)},
                          [user.email])


class UserProfileForm(forms.ModelForm):
    friendly_name = forms.CharField(label=_('Friendly Name'), required=False)
    full_name = forms.CharField(label=_('Full Name'), required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('friendly_name', 'full_name', 'avatar', 'email',
                  'timezone', 'language', 'country')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        self.new_email_pending = get_new_email_request(instance)
        if not config.ALLOW_CHANGE_PRIMARY_ADDRESS:
            self.fields['email'].disabled = True
            self.fields['email'].required = False
        else:
            if self.new_email_pending:
                self.fields['email'].disabled = True
                self.fields['email'].help_text = f'new email verification pending ({self.new_email_pending})'


class UserCreationForm(_UserCreationForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = forms.CharField(
        label=_('Password'),
        required=False,
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        required=False,
        widget=forms.PasswordInput,
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
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
        if self.cleaned_data['password1']:
            user.set_password(self.cleaned_data['password1'])
        else:
            user.set_unusable_password()

        if commit:
            user.save()
        return user


class NewMemberForm(_UserCreationForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    role = forms.ChoiceField(choices=Role.as_choices())

    password1 = forms.CharField(
        label=_('Password'),
        required=False,
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        required=False,
        widget=forms.PasswordInput,
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    class Meta:
        model = User
        fields = ('email', 'role',)

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
        if self.cleaned_data['password1']:
            user.set_password(self.cleaned_data['password1'])
        else:
            user.set_unusable_password()

        if commit:
            user.save()
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('id', 'user', 'label', 'address')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    # def has_changed(self):
    #     return super().has_changed()
    #
    # @cached_property
    # def changed_data(self):
    #     return super().changed_data


class AddressAssignmentForm(forms.ModelForm):
    class Meta:
        model = AddressAssignment
        fields = ('id', 'user', 'channel', 'address')
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _('Address assignment for this Channel already exists.'),
            }
        }

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)

        # choices = self.fields['dispatcher'].choices
        # self.fields['dispatcher'].choices = [c for c in choices[1:]]
        # self.fields['dispatcher'].choices = [c for c in choices[1:] if import_string(c[0]).subscription_class]
        request = state.request
        self.fields['address'].queryset = request.user.addresses.all()
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    def clean(self):
        super().clean()
        if self.cleaned_data:  # pragma: no branch
            channel = self.cleaned_data.get('channel', None)
            address = self.cleaned_data.get('address', None)
            if channel and address and address.address:
                try:
                    channel.validate_address(address.address)
                except DRFValidationError as e:
                    raise ValidationError({'address': ', '.join(e.detail)})
        return self.cleaned_data


AddressFormSetBase = forms.inlineformset_factory(User,
                                                 Address,
                                                 form=AddressForm,
                                                 min_num=1,
                                                 extra=0)
AddressAssignmentFormSetBase = forms.inlineformset_factory(User,
                                                           AddressAssignment,
                                                           form=AddressAssignmentForm,
                                                           min_num=1,
                                                           extra=0)


class AddressFormSet(AddressFormSetBase, BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(AddressFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.queryset.order_by('label')

    def save(self, commit=True):
        a = self.save_existing_objects(commit)
        b = self.save_new_objects(commit)
        return a + b


class AddressAssignmentFormSet(AddressAssignmentFormSetBase, BaseInlineFormSet):
    def save(self, commit=True):
        a = self.save_existing_objects(commit)
        b = self.save_new_objects(commit)
        return a + b

    def get_queryset(self):
        return super().get_queryset().order_by('channel')

    # def __init__(self, *args, **kwargs):
    #     super(AddressAssignmentFormSet, self).__init__(*args, **kwargs)
    #     self.queryset = self.queryset


class UserSubscriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        fields = ('subscriber', 'channel', 'event')


class UserSubscriptionBaseFormSet(BaseInlineFormSet):
    pass


UserSubscriptionFormSet = forms.inlineformset_factory(User,
                                                      Subscription,
                                                      form=UserSubscriptionForm,
                                                      formset=UserSubscriptionBaseFormSet,
                                                      min_num=0,
                                                      fk_name='subscriber',
                                                      extra=0)
