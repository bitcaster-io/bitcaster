# -*- coding: utf-8 -*-
"""
mercury / register
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from oath import from_b32key
from strategy_field.utils import fqn

from mercury.models import Organization, User
from mercury.models.organizationmember import OrganizationRole

from ..forms import RegistrationForm

logger = logging.getLogger(__name__)


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
            org.add_member(user, OrganizationRole.OWNER)
            user.send_confirmation_email()
            login(self.request, user, backend=fqn(ModelBackend))
            url = reverse('register-wait-email', args=[user.pk])
            return HttpResponseRedirect(url)


@require_http_methods(["GET", "POST"])
def confirm_email(request, pk, check):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.send_confirmation_email()
        url = reverse('register-wait-email', args=[user.pk])
        return HttpResponseRedirect(url)
    else:
        if user.is_active:
            return render(request, 'bitcaster/registration/already_registered.html')
        gauth = from_b32key(settings.OTP_KEY)
        ok = gauth.accept(check,
                          totp_forward_drift=int(settings.CONFIRM_EMAIL_EXPIRE / 30))
        if ok:
            user = User.objects.get(pk=pk)
            user.is_active = True
            user.save()
        ctx = {'valid': ok}
        return render(request, 'bitcaster/registration/email-confirmed.html', ctx)
    # if ratelimiter.is_limited(
    #         'auth:confirm-email:{}'.format(request.user.id),
    #         limit=10, window=60,  # 10 per minute should be enough for anyone
    # ):
    #     return HttpResponse(
    #         'You have made too many email confirmation requests. Please try again later.',
    #         content_type='text/plain',
    #         status=429,
    #     )
    #
    # if 'primary-email' in request.POST:
    #     email = request.POST.get('email')
    #     try:
    #         email_to_send = UserEmail.objects.get(user=request.user, email=email)
    #     except UserEmail.DoesNotExist:
    #         msg = _('There was an error confirming your email.')
    #         level = messages.ERROR
    #     else:
    #         request.user.send_confirm_email_singular(email_to_send)
    #         msg = _('A verification email has been sent to %s.') % (email)
    #         level = messages.SUCCESS
    #     messages.add_message(request, level, msg)
    #     return HttpResponseRedirect(reverse('sentry-account-settings'))
    # elif request.user.has_unverified_emails():
    #     request.user.send_confirm_emails()
    #     unverified_emails = [e.email for e in request.user.get_unverified_emails()]
    #     msg = _('A verification email has been sent to %s.') % (', ').join(unverified_emails)
    #     for email in unverified_emails:
    #         logger.info('user.email.start_confirm', extra={
    #             'user_id': request.user.id,
    #             'ip_address': request.META['REMOTE_ADDR'],
    #             'email': email,
    #         })
    # else:
    #     msg = _('Your email (%s) has already been verified.') % request.user.email
    # messages.add_message(request, messages.SUCCESS, msg)
    # return HttpResponseRedirect(reverse('sentry-account-settings-emails'))
