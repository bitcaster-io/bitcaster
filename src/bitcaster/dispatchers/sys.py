from typing import TYPE_CHECKING, Any

from django.core.mail import EmailMultiAlternatives, get_connection

from .base import Dispatcher, MessageProtocol, Payload

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import DispatcherHandler

    from ..models import Assignment


class SystemDispatcher(Dispatcher):
    slug = "system-email"
    verbose_name = "System Email"
    config_class = None
    backend = None
    protocol: MessageProtocol = MessageProtocol.EMAIL

    def get_connection(self) -> "DispatcherHandler":
        return get_connection()

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        subject: str = f"{self.channel.subject_prefix}{payload.subject or ''}"
        email = EmailMultiAlternatives(
            subject=subject,
            body=payload.message,
            from_email=self.channel.from_email,
            to=[address],
            connection=self.get_connection(),
        )
        if payload.html_message:
            email.attach_alternative(payload.html_message, "text/html")
        return email.send() > 0
