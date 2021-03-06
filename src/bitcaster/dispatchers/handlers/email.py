import smtplib
from logging import getLogger

from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, get_connection
from rest_framework import serializers

from bitcaster.api.fields import PasswordField
from bitcaster.exceptions import PluginSendError
from bitcaster.utils.reflect import fqn

from ..base import (CoreDispatcher, DispatcherOptions,
                    MessageType, SubscriptionOptions,)
from ..registry import dispatcher_registry

logger = getLogger(__name__)


class EmailMessage(MessageType):
    has_subject = True
    allow_html = True


class EmailSubscription(SubscriptionOptions):
    recipient = serializers.EmailField()


class EmailOptions(DispatcherOptions):
    server = serializers.CharField()
    port = serializers.IntegerField(default=25)
    username = serializers.CharField(allow_blank=True, required=False)
    password = PasswordField(allow_blank=True, required=False)
    tls = serializers.BooleanField(default=False)
    sender = serializers.EmailField(required=True)
    timeout = serializers.IntegerField(default=60)
    backend = serializers.CharField(default='django.core.mail.backends.smtp.EmailBackend')
    allow_attachments = serializers.BooleanField(required=False, default=False)


@dispatcher_registry.register
class Email(CoreDispatcher):
    icon = '/bitcaster/images/email-icon.png'
    options_class = EmailOptions
    subscription_class = EmailSubscription
    message_class = EmailMessage

    def _get_connection(self) -> object:
        config = self.config
        return get_connection(
            backend=self.config['backend'],
            host=config['server'],
            username=config.get('username', ''),
            password=config.get('password', ''),
            port=self.config['port'],
            use_tls=config['tls'],
            fail_silently=False)

    # def get_recipient_address(self, subscription):
    #     return super().get_recipient_address(subscription)

    def emit(self, address, subject, message, connection=None, attachments=None,
             html_message=None,
             *args, **kwargs) -> str:
        try:
            connection = connection or self._get_connection()
            mail = EmailMultiAlternatives(subject=subject,
                                          body=message,
                                          from_email=self.config['sender'],
                                          to=[address],
                                          connection=connection)
            if attachments:
                for attachment in attachments:
                    mail.attach(attachment.name, attachment.read(), attachment.content_type)
            if html_message:
                mail.attach_alternative(html_message, 'text/html')
            mail.send()
            self.logger.debug(f'{fqn(self)} email sent to {address}')
            return address
        except smtplib.SMTPException as e:  # pragma: no cover
            raise ValidationError(str(e)) from e
        except ValidationError as e:
            self.logger.exception(e)
            raise PluginSendError(e)
        except Exception as e:
            self.logger.exception(e)
            raise PluginSendError(e)

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
