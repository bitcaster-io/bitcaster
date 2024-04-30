import enum
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, cast

from django.core.exceptions import ValidationError
from django.forms import forms
from django.utils.functional import cached_property, classproperty
from django.utils.module_loading import import_string
from strategy_field.registry import Registry

from bitcaster.constants import AddressType

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, User
    from bitcaster.types.dispatcher import DispatcherHandler, TDispatcherConfig

logger = logging.getLogger(__name__)


class Capability(enum.IntEnum):
    HTML = 1
    TEXT = 2
    SUBJECT = 4


@enum.unique
class MessageProtocol(enum.IntEnum):
    PLAINTEXT = 100
    SMS = 200
    EMAIL = 300

    def has_capability(self, capability: Capability):
        return capability in ProtocolCapabilities[self]


ProtocolCapabilities = {
    MessageProtocol.PLAINTEXT: [Capability.TEXT],
    MessageProtocol.EMAIL: [Capability.SUBJECT, Capability.HTML, Capability.HTML],
    MessageProtocol.SMS: [Capability.TEXT],
}


class DispatcherMeta(type["Dispatcher"]):
    _all = {}
    _dispatchers = []

    def __new__(mcs: Type["Dispatcher"], class_name: str, bases: Tuple[Any], attrs: Dict[str, Any]) -> "Dispatcher":
        if attrs["__qualname__"] == "Dispatcher":
            return super().__new__(mcs, class_name, bases, attrs)

        if attrs["slug"].isnumeric():  # pragma: no cover
            raise ValueError(f'{class_name} Invalid Dispatcher.slug {attrs["slug"]}')
        if attrs["slug"] in mcs._all:  # pragma: no cover
            raise ValueError(f'{class_name} Duplicate Dispatcher.slug {attrs["slug"]}')

        cls = super().__new__(mcs, class_name, bases, attrs)
        if cls not in dispatcherManager:  # pragma: no branch
            dispatcherManager.register(cls)
        return cast(Dispatcher, cls)


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
        for k, v in kwargs.items():
            setattr(self, k, v)

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__


class DispatcherConfig(forms.Form):
    pass


class Dispatcher(metaclass=DispatcherMeta):
    slug = "--"
    verbose_name: str = ""
    config_class: "Type[DispatcherConfig]" = DispatcherConfig
    backend: "Optional[str, DispatcherHandler]" = None
    address_types: List[AddressType] = [AddressType.GENERIC]
    channel: "Channel"
    protocol: MessageProtocol = MessageProtocol.PLAINTEXT

    def __init__(self, channel: "Channel") -> None:
        self.channel = channel

    def get_connection(self) -> "DispatcherHandler":
        if isinstance(self.backend, str):
            klass = import_string(self.backend)
        else:
            klass = self.backend
        return klass(fail_silently=False, **self.config)

    @cached_property
    def config(self) -> Dict[str, Any]:
        cfg: "TDispatcherConfig" = self.config_class(data=self.channel.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return cfg.cleaned_data

    def send(self, address: str, payload: Payload) -> Optional[Any]: ...

    @classproperty
    def name(cls) -> str:
        return cls.verbose_name or cls.__name__.title()


class DispatcherManager(Registry):
    pass


dispatcherManager = DispatcherManager(Dispatcher)
