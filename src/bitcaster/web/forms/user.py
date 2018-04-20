# -*- coding: utf-8 -*-
import logging

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (AuthenticationForm as _AuthenticationForm,
                                       UserChangeForm as _UserChangeForm,
                                       UserCreationForm as _UserCreationForm,)
from django.forms import PasswordInput
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from bitcaster.db.fields import Role
from bitcaster.mail import send_mail_by_template
from bitcaster.models import Organization, User
from bitcaster.otp import totp
from bitcaster.utils.email_verification import get_new_email_request
from bitcaster.utils.http import absolute_uri

logger = logging.getLogger(__name__)


class UserRegistrationForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(widget=PasswordInput(attrs={'autocomplete': 'new-password'}))
    organization = forms.CharField(help_text=_("If you're signing up for a personal account, "
                                               "try using your own name."))
    billing_email = forms.EmailField(required=False,
                                     widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
                                     help_text=_("If provided, we will send all billing-related notifications "
                                                 "to this address."))
    terms = forms.BooleanField(label=_("I agree to the Terms of Service the Privacy Policy"))

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


class AuthenticationForm(_AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(widget=PasswordInput(attrs={'autocomplete': 'current-password'}))


class UserChangeForm(_UserChangeForm):
    last_password_change = forms.DateTimeField(disabled=True, required=False)
    date_joined = forms.DateTimeField(disabled=True, required=False)
    last_login = forms.DateTimeField(disabled=True, required=False)

    class Meta:
        model = User
        exclude = ('user_permissions', 'groups')


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
    friendly_name = forms.CharField(required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('friendly_name', 'avatar', 'email',
                  'timezone', 'language', 'country')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        self.new_email_pending = get_new_email_request(instance)
        if self.new_email_pending:
            self.fields['email'].disabled = True
            self.fields['email'].help_text = f'new email verification pending ({self.new_email_pending})'

    # def get_new_email_key(self):
    #     return f'new-email-{self.instance.pk}'

    # def save(self, commit=True):
        # email_changed = self.fields['email'].has_changed(self.initial.get('email'),
        #                                               self.data.get('email'))
        #
        # if email_changed:
        #     cache.set(self.get_new_email_key(), self.data['email'])
        #     send_address_verification_email(self.instance)
        #     self.instance.email = self.initial['email']
        # super().save(commit)
        # return self.instance
    # def clean_picture(self):
    #     picture = self.cleaned_data['picture']
    #     if picture:
    #     try:
    #         w, h = get_image_dimensions(picture)
    #
    #         # validate dimensions
    #         max_width = max_height = 100
    #         if w > max_width or h > max_height:
    #             raise forms.ValidationError(
    #                 u'Please use an image that is '
    #                 '%s x %s pixels or smaller.' % (max_width, max_height))
    #
    #         # validate content type
    #         main, sub = picture.content_type.split('/')
    #         if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
    #             raise forms.ValidationError(u'Please use a JPEG, '
    #                                         'GIF or PNG image.')
    #
    #         # validate file size
    #         if len(picture) > (20 * 1024):
    #             raise forms.ValidationError(
    #                 u'Avatar file size may not exceed 20k.')
    #
    #     except AttributeError:
    #         """
    #         Handles case when we are updating the user profile
    #         and do not supply a new avatar
    #         """
    #         pass
    #
    #     return picture


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


class NewMemberForm(_UserCreationForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    role = forms.ChoiceField(choices=Role.as_choices())

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
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        else:
            user.set_unusable_password()

        if commit:
            user.save()
        return user
