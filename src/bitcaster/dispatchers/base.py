import enum
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, cast

from django.core.exceptions import ValidationError
from django.db import models
from django.forms import forms
from django.utils.functional import cached_property, classproperty
from django.utils.module_loading import import_string
from strategy_field.registry import Registry

from bitcaster.constants import AddressType

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, User
    from bitcaster.types.dispatcher import DispatcherHandler, TDispatcherConfig

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

    def has_capability(self, capability: Capability) -> bool:
        return capability in ProtocolCapabilities[self]


ProtocolCapabilities = {
    MessageProtocol.PLAINTEXT: [Capability.TEXT],
    MessageProtocol.EMAIL: [Capability.SUBJECT, Capability.HTML, Capability.TEXT],
    MessageProtocol.SMS: [Capability.TEXT],
}


class Payload:
    message: str
    subject: str | None = None
    html_message: str | None = None
    event: "Event"
    user: Optional["User"] = None

    def __init__(
        self,
        message: str,
        event: "Event",
        user: "Optional[User]" = None,
        subject: str = "",
        html_message: str = "",
        **kwargs: Dict[str, Any],
    ):
        self.message = message
        self.event = event
        self.subject = subject
        self.html_message = html_message
        self.user = user


class DispatcherConfig(forms.Form):
    pass


class DispatcherMeta(type["Dispatcher"]):
    _all = {}
    # _dispatchers = []
    verbose_name: str = ""

    def __repr__(cls) -> str:
        return cls.verbose_name

    def __new__(mcs: Type["Dispatcher"], class_name: str, bases: Tuple[Any], attrs: Dict[str, Any]) -> "Dispatcher":
        if attrs["__qualname__"] == "Dispatcher":
            return super().__new__(mcs, class_name, bases, attrs)

        # if attrs["slug"].isnumeric():  # pragma: no cover
        #     raise ValueError(f'{class_name} Invalid Dispatcher.slug {attrs["slug"]}')
        # if attrs["slug"] in mcs._all:  # pragma: no cover
        #     raise ValueError(f'{class_name} Duplicate Dispatcher.slug {attrs["slug"]}')

        cls = super().__new__(mcs, class_name, bases, attrs)
        if cls not in dispatcherManager:  # pragma: no branch
            dispatcherManager.register(cls)
        return cast(Dispatcher, cls)


class Dispatcher(metaclass=DispatcherMeta):
    slug = "--"
    verbose_name: str = ""
    config_class: "Type[DispatcherConfig] | None" = DispatcherConfig
    backend: "Optional[str, DispatcherHandler]" = None
    address_types: List[AddressType] = [AddressType.GENERIC]
    channel: "Channel"
    protocol: MessageProtocol = MessageProtocol.PLAINTEXT

    def __init__(self, channel: "Channel") -> None:
        self.channel = channel

    def __repr__(self) -> str:
        return f"<Channel {self.verbose_name}>"

    def __str__(self) -> str:
        return self.verbose_name

    @cached_property
    def capabilities(self) -> list[Capability]:
        return ProtocolCapabilities[self.protocol]

    def get_connection(self) -> "DispatcherHandler":
        if isinstance(self.backend, str):
            klass = import_string(self.backend)
        else:
            klass = self.backend
        return klass(fail_silently=False, **self.config)

    @property
    def config(self) -> Dict[str, Any]:
        cfg: "TDispatcherConfig" = self.config_class(data=self.channel.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return cfg.cleaned_data

    @classproperty
    def name(cls) -> str:
        return cls.verbose_name or cls.__name__.title()

    def send(self, address: str, payload: Payload) -> bool:
        raise NotImplementedError


class DispatcherManager(Registry):
    pass


dispatcherManager = DispatcherManager(Dispatcher)
