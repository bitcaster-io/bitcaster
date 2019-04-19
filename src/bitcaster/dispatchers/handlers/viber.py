# -*- coding: utf-8 -*-
import time
from logging import getLogger

import six
from constance import config
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from sentry_sdk import capture_exception
from viberbot import Api, BotConfiguration
from viberbot.api.messages import TextMessage
from viberbot.api.viber_requests import (ViberMessageRequest,
                                         ViberSubscribedRequest,
                                         ViberUnsubscribedRequest,)

from bitcaster.api.fields import PasswordField, PhoneNumberField
from bitcaster.otp import OtpHandler
from bitcaster.utils import fqn
from bitcaster.utils.http import absolute_uri

from ..base import (CoreDispatcher, DispatcherOptions,
                    MessageType, SubscriptionOptions,)
from ..registry import dispatcher_registry

logger = getLogger(__name__)


class ViberMessage(MessageType):
    has_subject = False
    allow_html = False


class ViberSubscription(SubscriptionOptions):
    recipient = PhoneNumberField()


class ViberOptions(DispatcherOptions):
    account_name = serializers.CharField(help_text=_('Account Name'))
    uri = serializers.CharField(help_text=_('Uri'))
    # site = serializers.URLField(help_text=_('This server url.'),
    #                             initial=lambda: state.request.build_absolute_uri('/'))
    avatar = serializers.URLField(help_text=_('Account Image'),
                                  required=False, allow_blank=True)
    auth_token = PasswordField()


@dispatcher_registry.register
class Viber(CoreDispatcher):
    options_class = ViberOptions
    subscription_class = ViberSubscription
    message_class = ViberMessage
    need_verification = False
    icon = 'viber'
    __help__ = _("""Viber dispatcher to send private message

#### Get API keys

* Register at [[https://partners.viber.com/about]]
* Click on [Create Bot Account](https://partners.viber.com/account/create-bot-account)
* Copy the token and paste it here

""")

    def get_usage(self) -> object:
        info = {'qrcode': 'viber://pa/info?uri=%s' % self.config['uri'],
                'url': reverse('qrcode')}
        info.update(self.config)
        return _("""
* Open your Viber application and goto More->QR code
* Scan the following code and follow **%(account_name)s**
<div class="container">
<img class="mx-auto d-block m-3" src="%(url)s?text=%(qrcode)s" style="display:block">
</div>
* When ready click on **Send Code** and paste it here.
""") % dict(info)

    def _make_token_with_timestamp(self, user):
        ts_b36 = int_to_base36(int(time.time()))

        hash = salted_hmac(
            settings.SECRET_KEY,
            six.text_type(user.id) + six.text_type(ts_b36)
        ).hexdigest()[::2]
        return '%s-%s' % (ts_b36, hash)

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, hash = token.split('-')
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit. Timestamps are rounded to
        # midnight (server time) providing a resolution of only 1 day. If a
        # link is generated 5 minutes before midnight and used 6 minutes later,
        # that counts as 1 day. Therefore, PASSWORD_RESET_TIMEOUT_DAYS = 1 means
        # "at least 1 day, could be up to 2."
        if (self._num_days(self._today()) - ts) > 1:  # greater than 1 day
            return False

        return True

    def _get_connection(self) -> Api:
        config = self.config

        bot_configuration = BotConfiguration(
            name=config['account_name'],
            avatar=config['avatar'],
            auth_token=config['auth_token'],
        )
        return Api(bot_configuration)

    def registration(self, request):
        otp = request.GET.get('otp')
        messages, dt = OtpHandler().validate(otp)
        request.user.store(fqn(self), self.owner.pk, messages[0])
        address = request.user.assignments.get(channel=self.owner).address
        address.verified = True
        address.save()
        return HttpResponseRedirect('/')

    def callback(self, request):
        conn = self._get_connection()
        if not conn.verify_signature(request.body, request.META.get('X-Viber-Content-Signature')):
            logger.error('Viber 403: %s' % request.body)
        viber_request = conn.parse_request(request.body)

        if isinstance(viber_request, ViberUnsubscribedRequest):
            # viber_request.event_type == "unsubscribed"
            # viber_request.timestamp == int: milliseconds since epoch , eg 1554674273997
            # viber_request.user_id == str ... eg "qc7TSxYS+jiMst8pEYI56w=="
            try:
                # TODO: very inefficient way of retrieving the user
                from bitcaster.models import User
                user = None
                for u in User.objects.all():
                    if u.storage and u.retrieve(fqn(self), self.owner.pk) == viber_request.user_id:
                        user = u
                        break
                if user:
                    user.store(fqn(self), self.owner.pk, None)
            except Exception as e:
                capture_exception()
                logger.exception(e)
        elif isinstance(viber_request, ViberSubscribedRequest):
            otp = OtpHandler().get_otp(str(viber_request.user.id))
            url = absolute_uri(reverse('channel-registration', args=[self.owner.pk]))
            message = TextMessage(text='%s?otp=%s' % (url, otp.decode()))
            conn.send_messages(viber_request.user.id, [message])
            return HttpResponse()
        elif isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message
            conn.send_messages(viber_request.sender.id, [message])
        return HttpResponse()

    def get_recipient_address(self, subscription):
        if isinstance(subscription, str):
            raise ValueError(subscription)
        if hasattr(subscription, 'subscriber'):  # models.Subscription
            user = subscription.subscriber
        elif hasattr(subscription, 'assignments'):  # models.User
            user = subscription
        else:
            raise ValueError()
        return user.retrieve(fqn(self), self.owner.pk)
        # return user.assignments.get_address(self).address

    def emit(self, subscription, subject, message, connection=None, silent=True, *args, **kwargs) -> int:
        # recipient = subscription.subscriber.storage.get(fqn(self), None)
        recipient = self.get_recipient_address(subscription)
        try:
            conn = connection or self._get_connection()
            url = reverse('channel-callback', args=[self.owner.pk])
            cb = '%s%s' % (config.SITE_URL, url)
            conn.set_webhook(cb)

            text_message = TextMessage(text=message)
            conn.send_messages(recipient, text_message)
            self.logger.debug(f'{fqn(self)} sent to {recipient}')
            return 1
        except Exception as e:
            if silent:
                self.logger.exception(e)
            else:
                raise

    def test_connection(self, raise_exception=False) -> bool:
        try:
            self._get_connection()
            return True
        except Exception as e:
            self.logger.exception(e)
            if raise_exception:
                raise
            return False
