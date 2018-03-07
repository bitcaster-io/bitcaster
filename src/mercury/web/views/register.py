# -*- coding: utf-8 -*-
"""
mercury / register
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from strategy_field.utils import fqn

from mercury.db.fields import Role
from mercury.models import Organization, User

from ..forms import RegistrationForm

logger = logging.getLogger(__name__)

__all__ = ["UserRegister"]


class UserRegister(SingleObjectTemplateResponseMixin, FormView):
    template_name = 'bitcaster/users/register.html'
    model = User
    form_class = RegistrationForm
    success_url = reverse_lazy('register-wait-email')

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create(email=form.cleaned_data['email'],
                                       is_active=False,
                                       name=form.cleaned_data['name'],
                                       password=make_password(form.cleaned_data['password']),
                                       )
            org = Organization.objects.create(name=form.cleaned_data['organization'],
                                              billing_email=form.cleaned_data['billing_email'],
                                              owner=user
                                              )
            org.add_member(user, Role.OWNER)
            user.send_confirmation_email()
            login(self.request, user, backend=fqn(ModelBackend))
            url = reverse('register-wait-email', args=[user.pk])
            return HttpResponseRedirect(url)
