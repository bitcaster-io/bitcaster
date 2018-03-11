# -*- coding: utf-8 -*-
import smtplib

from django.core.exceptions import ValidationError
from django.core.mail import get_connection, send_mail
from rest_framework import serializers

from bitcaster.api.fields import PasswordField
from bitcaster.exceptions import PluginValidationError
from bitcaster.utils import fqn

from .base import (Dispatcher, DispatcherOptions,
                   MessageType, SubscriptionOptions,)
from .registry import dispatcher_registry

# logger = getLogger(__name__)


class EmailMessage(MessageType):
    pass


class EmailSubscription(SubscriptionOptions):
    email = serializers.EmailField()


class EmailOptions(DispatcherOptions):
    server = serializers.CharField()
    port = serializers.IntegerField()
    username = serializers.CharField(allow_blank=True, required=False)
    password = PasswordField(allow_blank=True, required=False)
    tls = serializers.BooleanField(default=False)
    sender = serializers.EmailField(required=True)
    timeout = serializers.IntegerField(default=60)
    backend = serializers.CharField(default='django.core.mail.backends.smtp.EmailBackend')


@dispatcher_registry.register
class Email(Dispatcher):
    __core__ = True
    options_class = EmailOptions
    subscription_class = EmailSubscription
    message_class = EmailMessage

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        cfg = {'email': self.owner.config.get('email', subscription.subscriber.email)}
        try:
            return self.subscription_class(data=cfg).is_valid(True)
        except (serializers.ValidationError, ValidationError) as e:
            raise PluginValidationError(str(e)) from e

    def _get_connection(self) -> object:
        config = self.config
        return get_connection(
            backend=self.config['backend'],
            host=config["server"],
            username=config.get("username", ""),
            password=config.get("password", ""),
            port=self.config["port"],
            use_tls=config["tls"],
            fail_silently=False)

    def emit(self, subscription, subject, message, connection=None, *args, **kwargs):
        recipient = subscription.subscriber
        try:
            connection = connection or self._get_connection()
            ret = send_mail(subject=subject,
                            message=message,
                            connection=connection,
                            from_email=self.config["sender"],
                            recipient_list=[recipient.email])
            self.logger.debug("{0} email sent to {1.email}".format(fqn(self), recipient))
            return ret
        except smtplib.SMTPException as e:
            raise ValidationError(str(e)) from e
        except ValidationError as e:
            self.logger.exception(e)
        except Exception as e:
            self.logger.exception(e)

    def test_connection(self, raise_exception=False):
        try:
            conn = self._get_connection()
            conn.open()
            conn.close()
            return True
        except Exception as e:
            self.logger.exception(e)
            if raise_exception:
                raise
            return False
