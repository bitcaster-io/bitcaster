# -*- coding: utf-8 -*-
import logging

from constance import config
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from bitcaster.models import User
from bitcaster.otp import totp
from bitcaster.utils.email_verification import clear_new_email_request

logger = logging.getLogger(__name__)


#
# @require_http_methods(["GET", "POST"])
# def invitation_accept(request, pk, check):
#     if request.method == 'GET':
#         if totp.verify(check, config.INVITATION_EXPIRE/60):
#             membership = OrganizationMember.objects.get(pk=pk)
#             render(request, 'bitcaster/user_invite_register.html', )

@require_http_methods(['GET', 'POST'])
def confirm_registration(request, pk, check):
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


@require_http_methods(['GET', 'POST'])
def confirm_address(request, pk, address, check):
    ok = totp.verify(check, valid_window=config.INVITATION_EXPIRE)
    if ok:
        user = User.objects.get(pk=pk)
        user.email = address
        user.save()
        clear_new_email_request(user)
    return HttpResponseRedirect(reverse('user-profile'))
