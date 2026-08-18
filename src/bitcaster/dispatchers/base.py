from typing import TYPE_CHECKING, Any, cast

import abc
import enum
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.forms import forms
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property, classproperty
from django.utils.module_loading import import_string
from strategy_field.registry import Registry
from strategy_field.utils import fqn

from bitcaster.constants import AddressType
from bitcaster.exceptions import DispatcherError

if TYPE_CHECKING:
    from bitcaster.models import Assignment, Channel, Event, User
    from bitcaster.types.dispatcher import DispatcherHandler, TDispatcherConfig_co

logger = logging.getLogger(__name__)


class Capability(enum.StrEnum):
    HTML = "HTML"
    TEXT = "TEXT"
    SUBJECT = "SUBJECT"
    MARKDOWN = "MARKDOWN"


@enum.unique
class MessageProtocol(models.TextChoices):
    PLAINTEXT = "PLAINTEXT"
    SLACK = "SLACK"
    SMS = "SMS"
    EMAIL = "EMAIL"
    WEBPUSH = "WEBPUSH"
    INTERNAL = "INTERNAL"
    MARKDOWN = "MARKDOWN"

    def has_capability(self, capability: Capability) -> bool:
        return capability in ProtocolCapabilities[self]


ProtocolCapabilities = {
    MessageProtocol.PLAINTEXT: [Capability.TEXT],
    MessageProtocol.EMAIL: [Capability.SUBJECT, Capability.HTML, Capability.TEXT],
    MessageProtocol.SMS: [Capability.TEXT],
    MessageProtocol.WEBPUSH: [Capability.SUBJECT, Capability.TEXT],
    MessageProtocol.INTERNAL: [Capability.SUBJECT, Capability.HTML],
    MessageProtocol.MARKDOWN: [Capability.SUBJECT, Capability.MARKDOWN],
}


class Payload:
    message: str
    level: int = logging.INFO
    subject: str | None = None
    html_message: str | None = None
    event: "Event"
    user: "User | None" = None

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
            "user": self.user.username if self.user else "",
        }


class DispatcherConfig(forms.Form):
    help_text = ""

    def save(self, channel: "Channel") -> None:
        channel.config = self.cleaned_data
        channel.save()


class DispatcherMeta(abc.ABCMeta):
    _all = {}
    verbose_name: str = ""

    def __repr__(cls) -> str:
        return cls.verbose_name

    def __new__(cls: type["Dispatcher"], class_name: str, bases: tuple[Any], attrs: dict[str, Any]) -> "Dispatcher":
        if attrs["__qualname__"] == "Dispatcher":
            return super().__new__(cls, class_name, bases, attrs)
        new_cls = super().__new__(cls, class_name, bases, attrs)
        if not attrs.get("abstract", False) and new_cls not in dispatcherManager:  # pragma: no branch
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

    @abc.abstractmethod
    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        raise NotImplementedError

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        try:
            return self._send(address, payload, assignment, **kwargs)
        except DispatcherError:
            raise
        except Exception as e:
            raise DispatcherError(f"Error sending message: {e}") from e

    def subscribe(self, assignment: "Assignment", **kwargs: Any) -> HttpResponseRedirect:
        return HttpResponseRedirect(".")


class DispatcherManager(Registry):
    _choices: list[tuple[str, str]] | None

    def get_name(self, entry: type) -> str:
        if hasattr(entry, "verbose_name"):
            attr = entry.verbose_name
            if not attr:
                return fqn(entry)
            if callable(attr):
                return str(attr())
            return str(attr)
        return fqn(entry)

    def as_choices(self) -> list[tuple[str, str]]:
        if not self._choices:
            super().as_choices()
            self._choices = sorted(self._choices or [], key=lambda x: x[1])
        return self._choices


dispatcherManager = DispatcherManager(Dispatcher)  # noqa N816
