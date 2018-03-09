# -*- coding: utf-8 -*-
"""
bitcaster / callbacks
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from constance import config
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from bitcaster.models import User
from bitcaster.otp import totp

logger = logging.getLogger(__name__)


#
# @require_http_methods(["GET", "POST"])
# def invitation_accept(request, pk, check):
#     if request.method == 'GET':
#         if totp.verify(check, config.INVITATION_EXPIRE/60):
#             membership = OrganizationMember.objects.get(pk=pk)
#             render(request, 'bitcaster/user_invite_register.html', )


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
        ok = totp.verify(check, valid_window=config.INVITATION_EXPIRE)
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
