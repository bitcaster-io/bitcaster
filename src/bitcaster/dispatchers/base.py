import enum
import logging
from typing import TYPE_CHECKING, Any, Optional, cast

from django.core.exceptions import ValidationError
from django.db import models
from django.forms import forms
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property, classproperty
from django.utils.module_loading import import_string
from strategy_field.registry import Registry

from bitcaster.constants import AddressType

if TYPE_CHECKING:
    from bitcaster.models import Assignment, Channel, Event, User
    from bitcaster.types.dispatcher import DispatcherHandler, TDispatcherConfig_co

logger = logging.getLogger(__name__)


class Capability(enum.StrEnum):
    HTML = "HTML"
    TEXT = "TEXT"
    SUBJECT = "SUBJECT"


@enum.unique
class MessageProtocol(models.TextChoices):
    PLAINTEXT = "PLAINTEXT"
    SLACK = "SLACK"
    SMS = "SMS"
    EMAIL = "EMAIL"
    WEBPUSH = "WEBPUSH"
    INTERNAL = "INTERNAL"

    def has_capability(self, capability: Capability) -> bool:
        return capability in ProtocolCapabilities[self]


ProtocolCapabilities = {
    MessageProtocol.PLAINTEXT: [Capability.TEXT],
    MessageProtocol.EMAIL: [Capability.SUBJECT, Capability.HTML, Capability.TEXT],
    MessageProtocol.SMS: [Capability.TEXT],
    MessageProtocol.WEBPUSH: [Capability.SUBJECT, Capability.TEXT],
    MessageProtocol.INTERNAL: [Capability.SUBJECT, Capability.HTML],
}


class Payload:
    message: str
    level: int = logging.INFO
    subject: str | None = None
    html_message: str | None = None
    event: "Event"
    user: Optional["User"] = None

    def __init__(
        self,
        message: str,
        event: "Event",
        user: "User | None" = None,
        subject: str = "",
        html_message: str = "",
        **kwargs: dict[str, Any],
    ):
        self.message = message
        self.event = event
        self.subject = subject
        self.html_message = html_message
        self.user = user

    def as_dict(self) -> dict[str, str]:
        return {
            "message": self.message or "",
            "subject": self.subject or "",
            "html_message": self.html_message or "",
            "user": self.user.username,
        }


class DispatcherConfig(forms.Form):
    help_text = ""

    def save(self, channel: "Channel") -> None:
        channel.config = self.cleaned_data
        channel.save()


class DispatcherMeta(type["Dispatcher"]):
    _all = {}
    verbose_name: str = ""

    def __repr__(cls) -> str:
        return cls.verbose_name

    def __new__(cls: type["Dispatcher"], class_name: str, bases: tuple[Any], attrs: dict[str, Any]) -> "Dispatcher":
        if attrs["__qualname__"] == "Dispatcher":
            return super().__new__(cls, class_name, bases, attrs)
        new_cls = super().__new__(cls, class_name, bases, attrs)
        if new_cls not in dispatcherManager:  # pragma: no branch
            dispatcherManager.register(new_cls)
        return cast("Dispatcher", new_cls)


class Dispatcher(metaclass=DispatcherMeta):
    slug = "--"
    verbose_name: str = ""
    config_class: "type[DispatcherConfig] | None" = DispatcherConfig
    backend: "Any | None" = None
    address_types: list[AddressType] = [AddressType.GENERIC]
    channel: "Channel"
    protocol: MessageProtocol = MessageProtocol.PLAINTEXT
    need_subscription = False
    default_config: dict[str, Any] = {}

    def __init__(self, channel: "Channel") -> None:
        self.channel = channel

    def __repr__(self) -> str:
        return f"<Dispatcher {self.verbose_name}>"

    def __str__(self) -> str:
        return self.verbose_name or self.__class__.__name__

    @cached_property
    def capabilities(self) -> list[Capability]:
        return ProtocolCapabilities[self.protocol]

    def get_connection(self) -> "DispatcherHandler":
        if isinstance(self.backend, str):
            klass = import_string(self.backend)
        else:
            klass = self.backend
        logger.debug(f"Dispacther: {klass} creating connection with config {self.config}")
        return klass(fail_silently=False, **self.config)

    @property
    def config(self) -> dict[str, Any]:
        cfg: "TDispatcherConfig_co" = self.config_class(data=self.channel.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return cfg.cleaned_data

    def get_extra_config_info(self) -> str:
        return ""

    @classproperty
    def name(self) -> str:
        return self.verbose_name or self.__name__.title()

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        raise NotImplementedError

    def subscribe(self, assignment: "Assignment", **kwargs: Any) -> HttpResponseRedirect:
        return HttpResponseRedirect(".")


class DispatcherManager(Registry):
    pass


dispatcherManager = DispatcherManager(Dispatcher)  # noqa N816
