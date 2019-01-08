# -*- coding: utf-8 -*-
import json
import logging

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import escape, format_html, format_html_join, html_safe
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from rest_framework.exceptions import ValidationError as DRFValidationError

from bitcaster.models import Address, Organization, User
from bitcaster.utils.email_verification import set_new_email_request
from bitcaster.utils.wsgi import get_client_ip
from bitcaster.web.forms.user import send_address_verification_email

from ..forms import UserProfileForm
from .base import (BitcasterBaseDetailView,
                   BitcasterBaseUpdateView, BitcasterTemplateView,)

logger = logging.getLogger(__name__)

__all__ = ('UserProfileView', 'UserWelcomeView', 'UserHomeView', 'UserAddressesView')


class UserIndexView(TemplateView):
    template_name = 'bitcaster/me/home.html'


class UserHomeView(BitcasterBaseDetailView):
    template_name = 'bitcaster/users/user-home.html'
    model = User

    @cached_property
    def selected_organization(self):
        return Organization.objects.get(slug=self.kwargs['org'],
                                        members=self.request.user,
                                        )

    @cached_property
    def selected_application(self):
        return self.selected_organization.applications.get(slug=self.kwargs['app'])

    def get_context_data(self, **kwargs):
        kwargs['application'] = self.selected_application
        allowed_applications = []
        for m in self.request.user.memberships.all():
            for application in m.organization.applications.all():
                allowed_applications.append(
                    (m.organization, application)
                )
        return super().get_context_data(**kwargs)

    def get_object(self, queryset=None):
        return self.request.user


class UserWelcomeView(BitcasterTemplateView):
    template_name = 'bitcaster/users/user-welcome.html'


@html_safe
class FlatErrorList(ErrorList):
    """
    A collection of errors that knows how to display itself in various formats.
    """

    def __init__(self, initlist=None, error_class=None):
        super().__init__(initlist)

        if error_class is None:
            self.error_class = 'errorlist'
        else:
            self.error_class = 'errorlist {}'.format(error_class)

    def as_data(self):
        return ValidationError(self.data).error_list

    def get_json_data(self, escape_html=False):
        errors = []
        for error in self.as_data():
            message = next(iter(error))
            errors.append({
                'message': escape(message) if escape_html else message,
                'code': error.code or '',
            })
        return errors

    def as_json(self, escape_html=False):
        return json.dumps(self.get_json_data(escape_html))

    def as_ul(self):
        if not self.data:
            return ''

        return format_html(
            '<ul class="{}">{}</ul>',
            self.error_class,
            format_html_join('', '<li>{}</li>', ((e,) for e in self))
        )

    def as_text(self):
        return '\n'.join('* %s' % e for e in self)

    def __str__(self):
        return self.as_ul()

    def __repr__(self):
        return repr(list(self))

    def __contains__(self, item):
        return item in list(self)

    def __eq__(self, other):
        return list(self) == other

    def __getitem__(self, i):
        error = self.data[i]
        if isinstance(error, ValidationError):
            return next(iter(error))
        return error

    def __reduce_ex__(self, *args, **kwargs):
        # The `list` reduce function returns an iterator as the fourth element
        # that is normally used for repopulating. Since we only inherit from
        # `list` for `isinstance` backward compatibility (Refs #17413) we
        # nullify this iterator as it would otherwise result in duplicate
        # entries. (Refs #23594)
        info = super().__reduce_ex__(*args, **kwargs)
        return info[:3] + (None, None)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('id', 'user', 'dispatcher', 'address')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        choices = self.fields['dispatcher'].choices
        self.fields['dispatcher'].choices = [c for c in choices[1:] if import_string(c[0]).subscription_class]

    def clean(self):
        dispatcher = import_string(self.cleaned_data['dispatcher'])
        address = self.cleaned_data['address']
        try:
            dispatcher.validate_address(address)
        except DRFValidationError as e:
            raise ValidationError({'address': ', '.join(e.detail)})
        return super().clean()


# class SubscriptionBaseFormSet(BaseInlineFormSet):
#
#     def __init__(self, *args, **kwargs):
#         self.event = kwargs.pop('event')
#         super().__init__(*args, **kwargs)
#         self.form_kwargs['event'] = self.event


AddressFormSet = forms.inlineformset_factory(User,
                                             Address,
                                             form=AddressForm,
                                             # formset=SubscriptionBaseFormSet,
                                             min_num=1,
                                             extra=0)


class UserAddressesView(BitcasterBaseUpdateView):
    template_name = 'bitcaster/users/addresses.html'
    model = Address
    form_class = AddressForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('user-addresses')

    def get_form_class(self):
        return AddressFormSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        formset.instance = self.request.user
        formset.save()
        self.message_user('Addresses updated', messages.SUCCESS)
        return super().form_valid(formset)


class UserProfileView(BitcasterBaseUpdateView):
    template_name = 'bitcaster/users/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = '.'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)

        if ret['form'].new_email_pending:
            ret['newemail'] = ret['form'].new_email_pending
        return ret

    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        if not user.language:
            initial['language'] = self.request.LANGUAGE_CODE

        if not user.country or user.timezone:
            remote_ip = get_client_ip(self.request)
            if remote_ip:
                from geolite2 import geolite2
                reader = geolite2.reader()
                match = reader.get(remote_ip)
                if match:
                    if not user.country:
                        try:
                            initial['country'] = match['country']['iso_code']
                        except KeyError:
                            initial['country'] = None

                    if not user.timezone:
                        try:
                            initial['timezone'] = match['location']['time_zone']
                        except KeyError:
                            initial['timezone'] = None
        return initial

    def form_valid(self, form):
        email_changed = form.fields['email'].has_changed(form.initial.get('email'),
                                                         form.data.get('email'))

        if email_changed:
            set_new_email_request(form.instance, form.data['email'])
            send_address_verification_email(form.instance)
            form.instance.email = form.initial['email']
            self.message_user(_('Check your inbox to validate your new email address'), messages.SUCCESS)
        ret = super().form_valid(form)
        self.message_user(_('Profile Updated'), messages.SUCCESS)
        return ret
