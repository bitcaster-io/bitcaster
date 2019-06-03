import logging

from constance import config
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from bitcaster.models import Notification, Occurence, Subscription, User
from bitcaster.otp import totp
from bitcaster.utils.email_verification import clear_new_email_address_request

logger = logging.getLogger(__name__)


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
        clear_new_email_address_request(user)
    return HttpResponseRedirect(reverse('user-profile'))


@require_http_methods(['GET', 'POST'])
def pixel(request, **kwargs):
    return HttpResponse('Confirmed')


@require_http_methods(['GET', 'POST'])
def confirmation(request, event, subscription, channel, occurence, code):
    subscription = Subscription.objects.get(pk=subscription,
                                            event_id=event,
                                            channel_id=channel)
    Occurence.objects.get(pk=occurence)

    if code == subscription.get_code():
        ok = Notification.objects.filter(occurence_id=occurence,
                                         event_id=event,
                                         expired=False,
                                         confirmed__isnull=True,
                                         need_confirmation=True).update(confirmed=timezone.now())
        return HttpResponse(f'Confirmed {ok}')
    else:
        return HttpResponse(f'Error {code} {subscription.get_code()}', status=400)
