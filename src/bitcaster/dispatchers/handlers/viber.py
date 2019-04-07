# -*- coding: utf-8 -*-
import time
from logging import getLogger

import six
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from viberbot import Api, BotConfiguration
# from viberbot.api.messages import TextMessage
from viberbot.api.viber_requests import (ViberMessageRequest,
                                         ViberSubscribedRequest,
                                         ViberUnsubscribedRequest,)

from bitcaster.api.fields import PhoneNumberField
from bitcaster.otp import OtpHandler
from bitcaster.state import state
from bitcaster.utils import fqn

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
    application_name = serializers.CharField(help_text=_('Application Name'),
                                             initial='Bitcaster')
    site = serializers.URLField(help_text=_('This server url.'),
                                initial=lambda: state.request.build_absolute_uri('/'))
    avatar = serializers.URLField(help_text=_('URL of image to use as avatar'),
                                  required=False)
    auth_token = serializers.CharField()
    account_id = serializers.CharField()


@dispatcher_registry.register
class Viber(CoreDispatcher):
    options_class = ViberOptions
    subscription_class = ViberSubscription
    message_class = ViberMessage
    __help__ = _("""Viber dispatcher to send private message
    ### Get API keys
    - Register at https://partners.viber.com/login
    - Click on [Create Bot Account](https://partners.viber.com/account/create-bot-account)
    - Copy the token into the specific field
    """)

    # def validate_subscription(self, subscription, *args, **kwargs) -> bool:
    #     email = self.get_recipient_address(subscription)
    #     cfg = {'recipient': self.owner.config.get('recipient', email)}
    #     try:
    #         return self.subscription_class(data=cfg).is_valid(True)
    #     except (serializers.ValidationError, ValidationError) as e:
    #         raise PluginValidationError(str(e)) from e

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
        if (self._num_days(self._today()) - ts) > 1: # greater than 1 day
            return False

        return True

    def _get_connection(self) -> Api:
        config = self.config

        bot_configuration = BotConfiguration(
            name=config['application_name'],
            avatar=config['avatar'],
            auth_token=config['auth_token'],
        )
        return Api(bot_configuration)

    def registration(self, request):
        otp = request.GET['otp']
        # TODO: remove me
        print('1111111111', 'viber.py:75', 'Here we get the OTP and update user with the id encoded in the OTP')
        messages, dt = OtpHandler().validate(otp)
        # TODO: remove me
        print('1111111111', 'viber.py:127', f'messages[0] is user id: {messages[0]}')
        return HttpResponse()

    def callback(self, request):
        conn = self._get_connection()
        if not conn.verify_signature(request.body, request.META.get('X-Viber-Content-Signature')):
            logger.error('Viber 403')
        viber_request = conn.parse_request(request.body)
        # TODO: remove me
        print(111, 'viber.py:79', 2222222, viber_request, type(viber_request))
        if isinstance(viber_request, ViberUnsubscribedRequest):
            pass
        elif isinstance(viber_request, ViberSubscribedRequest):
            otp = OtpHandler().get_otp(str(viber_request.user.id))
            url = reverse('callback_registration', kwargs={'otp', otp})

            # TODO: remove me
            print(111, 'viber.py:84', 'What do we do here?')
            return url
        elif isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message
            # TODO: remove me
            print(111, 'viber.py:88', viber_request.sender)
            print(111, 'viber.py:89', viber_request.sender.id)
            conn.send_messages(viber_request.sender.id, [message])
        return HttpResponse()

    def emit(self, subscription, subject, message, connection=None, silent=True, *args, **kwargs) -> int:
        recipient = self.get_recipient_address(subscription)
        try:
            conn = connection or self._get_connection()
            url = reverse('channel-callback', args=[self.owner.pk])
            cb = '%s%s' % (self.config['site'], url)
            # TODO: remove me
            print(111, 'viber.py:93', 111111, recipient)
            conn.set_webhook(cb)

            # ## text_message = TextMessage(text=message)
            # ## sent_messages_tokens = conn.send_messages(recipient, text_message)
            self.logger.debug(f'{fqn(self)} sent to {recipient}')
            return 1
        except Exception as e:
            if silent:
                self.logger.exception(e)
            else:
                raise

    def test_connection(self, raise_exception=False) -> bool:
        try:
            conn = self._get_connection()
            conn.ensure_session()
            return True
        except Exception as e:
            self.logger.exception(e)
            if raise_exception:
                raise
            return False
