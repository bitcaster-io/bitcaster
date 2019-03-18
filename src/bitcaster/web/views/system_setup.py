# -*- coding: utf-8 -*-
from constance import config
from django import forms
from django.contrib.auth import login, password_validation
from django.contrib.auth.backends import ModelBackend
from django.db import transaction
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, ProcessFormView
from strategy_field.utils import fqn

from bitcaster.framework.db.fields import Role
from bitcaster.models import Organization, User
# from bitcaster.models.configurationissue import check_organization
from bitcaster.models.organization import RESERVED_ORGANIZATION_NAME
from bitcaster.models.validators import ListValidator, NameValidator

__all__ = ['SetupView']


class SetupForm(forms.Form):
    error_messages = {'password_mismatch': _('Passwords do not match')}

    organization = forms.CharField(validators=[ListValidator(RESERVED_ORGANIZATION_NAME),
                                               NameValidator(),
                                               ])
    email = forms.EmailField()
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class SetupView(TemplateView, FormMixin, ProcessFormView):
    template_name = 'bitcaster/setup.html'
    form_class = SetupForm
    success_url = '/'

    def get(self, request, *args, **kwargs):
        if bool(config.INITIALIZED):
            return HttpResponseNotFound('Not Found')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            organization = form.cleaned_data['organization']
            user = User.objects.create_superuser(form.cleaned_data['email'],
                                                 form.cleaned_data['password1'])
            org = Organization.objects.create(name=organization,
                                              slug=slugify(organization),
                                              admin_email=user.email,
                                              is_core=True,
                                              owner=user)
            org.add_member(user, role=Role.OWNER, date_enrolled=timezone.now())
            # org.teams.create(name='Owners', manager=user)

            # check_organization(org)
            config.SYSTEM_CONFIGURED = 0
            config.INITIALIZED = 1
            login(self.request, user, fqn(ModelBackend))
        return super().form_valid(form)
