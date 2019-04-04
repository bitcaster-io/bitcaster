# -*- coding: utf-8 -*-
import logging

from constance import config
from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
    UserCreationForm as _UserCreationForm,)
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms import BaseInlineFormSet, PasswordInput
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_countries import countries
from rest_framework.exceptions import ValidationError as DRFValidationError
from timezone_field import TimeZoneField

from bitcaster.framework.db.fields import ROLES
from bitcaster.framework.forms.fields import generic
from bitcaster.mail import send_mail_by_template
from bitcaster.models import (Address, AddressAssignment,
                              Channel, Subscription, User,)
from bitcaster.otp import totp
from bitcaster.state import state
from bitcaster.utils.email_verification import check_new_email_address_request
from bitcaster.utils.http import absolute_uri

logger = logging.getLogger(__name__)


class AuthenticationForm(_AuthenticationForm):
    # username = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    username = forms.CharField()
    password = forms.CharField(widget=PasswordInput(attrs={'autocomplete': 'current-password'}))


class UserInviteRegistrationForm(forms.ModelForm):
    email = forms.EmailField(disabled=True)
    password = forms.CharField(widget=PasswordInput(attrs={'autocomplete': 'new-password'}))

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
    name = forms.CharField(label=_('Full Name'), required=False)
    email = forms.EmailField()
    timezone = generic.Select2ChoiceField(choices=TimeZoneField.CHOICES)
    language = generic.Select2ChoiceField(choices=settings.LANGUAGES)
    country = generic.Select2ChoiceField(choices=countries)

    class Meta:
        model = User
        fields = ('friendly_name', 'name', 'avatar', 'email',
                  'timezone', 'language', 'country')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        self.new_email_pending = check_new_email_address_request(instance)
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
    role = forms.ChoiceField(choices=ROLES)

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
    label = generic.CharField(hint='email,mobile')
    address = generic.CharField(hint='me@email.com')

    class Meta:
        model = Address
        fields = ('id', 'user', 'label', 'address')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class AddressAssignmentForm(forms.ModelForm):
    # address = forms.ModelChoiceField(queryset=Address.objects.all(),
    #                                  widget=ModelSelect2(url='address-autocomplete')
    #                                  )
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
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.order_by('label')

    def save(self, commit=True):
        a = self.save_existing_objects(commit)
        b = self.save_new_objects(commit)
        return a + b


class AddressAssignmentFormSet(AddressAssignmentFormSetBase, BaseInlineFormSet):
    disabled_subscriptions = None

    def save(self, commit=True):
        a = self.save_existing_objects(commit)
        b = self.save_new_objects(commit)
        return a + b

    def delete_existing(self, obj, commit=True):
        # disable all subscriptions that use this address
        self.disabled_subscriptions = obj.channel.linked_subscriptions.filter(subscriber=obj.user,
                                                                              enabled=True).update(enabled=False)
        super().delete_existing(obj, commit)

    def get_queryset(self):
        return super().get_queryset().order_by('channel')


class UserSubscribeForm(forms.Form):
    # recipient = forms.CharField(required=False)
    # channels = forms.MultipleChoiceField()
    channels = forms.ModelMultipleChoiceField(queryset=Channel.objects.none())

    def __init__(self, instance, **kwargs):
        self.event = instance
        super().__init__(**kwargs)
        self.fields['channels'].queryset = self.event.channels.filter(addresses__user=state.request.user)


class UserSubscriptionEditForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('channel',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['channel'].queryset = self.instance.event.channels.filter(addresses__user=state.request.user)

    def clean_channel(self):
        value = self.cleaned_data['channel']
        # this form i sonly for edit
        qs = Subscription.objects.filter(subscriber=self.instance.subscriber,
                                         event=self.instance.event,
                                         channel=value).exclude(id=self.instance.pk)

        if qs.exists():
            raise ValidationError(_('This channel is already used.'))
        return value
