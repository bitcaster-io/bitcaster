# -*- coding: utf-8 -*-
import smtplib
from django.core.mail import get_connection

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mercury.logging import getLogger
from mercury.utils import fqn

from .base import (Dispatcher, DispatcherOptions,
                   MessageType, SubscriptionOptions,)
from .registry import dispatcher_registry

logger = getLogger(__name__)


class EmailMessage(MessageType):
    pass


class EmailSubscription(SubscriptionOptions):
    email = serializers.EmailField()


class EmailOptions(DispatcherOptions):
    server = serializers.CharField()
    port = serializers.IntegerField()
    username = serializers.CharField(allow_blank=True, required=False)
    password = serializers.CharField(allow_blank=True, required=False)
    tls = serializers.BooleanField(default=False)
    sender = serializers.EmailField(required=True)
    timeout = serializers.IntegerField(default=1)


@dispatcher_registry.register
class Email(Dispatcher):
    options_class = EmailOptions
    subscription_class = EmailSubscription
    message_class = EmailMessage

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        if not subscription.subscriber.email:
            raise ValidationError("")

    def _get_connection(self):
        config = self.config
        return get_connection(
            # backend='django.core.mail.backends.smtp.EmailBackend',
            host=config["server"],
            username=config.get("username", ""),
            password=config.get("password", ""),
            port=self.config["port"],
            use_tls=config["tls"],
            fail_silently=False)

    def emit(self, subscription, subject, message, *args, **kwargs):
        from django.core.mail import send_mail
        recipient = subscription.subscriber
        try:
            conn = self._get_connection()
            ret = send_mail(subject=subject,
                            message=message,
                            connection=conn,
                            from_email=self.config["sender"],
                            recipient_list=[recipient.email])
            logger.debug("{0} email sent to {1.email}".format(fqn(self), recipient))
            return ret
        except smtplib.SMTPException as e:
            raise ValidationError(str(e)) from e
        except ValidationError as e:
            logger.exception(e)
            raise
        except Exception as e:
            logger.exception(e)
            raise

    def test_message(self, subscription, subject, message, *args, **kwargs):
        # assert subscription.event is None
        assert subscription.pk is None
        return self.emit(subscription, subject, message, *args, **kwargs)

    def test_connection(self, raise_exception=False):
        try:
            conn = self._get_connection()
            conn.open()
            conn.close()
            return True
        except Exception as e:
            logger.exception(e)
            if raise_exception:
                raise
            return False
