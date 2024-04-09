import logging
from typing import TYPE_CHECKING, Any, Dict, Tuple, Type, cast

from django.forms import forms
from django.utils.functional import classproperty
from strategy_field.registry import Registry

if TYPE_CHECKING:
    from bitcaster.models import Channel, EventType, User

logger = logging.getLogger(__name__)


class DispatcherMeta(type["Dispatcher"]):
    _all = {}
    _dispatchers = []

    def __new__(mcs: Type["Dispatcher"], class_name: str, bases: Tuple[Any], attrs: Dict[str, Any]) -> "Dispatcher":
        if attrs["__qualname__"] == "Dispatcher":
            return super().__new__(mcs, class_name, bases, attrs)

        if attrs["id"] in mcs._all:  # pragma: no cache
            raise ValueError(f'{class_name} Duplicate Dispatcher.id {attrs["id"]}')
        elif attrs["slug"] in mcs._all:  # pragma: no cache
            raise ValueError(f'{class_name} Duplicate Dispatcher.slug {attrs["slug"]}')
        elif attrs["slug"].isnumeric():  # pragma: no cache
            raise ValueError(f'{class_name} Invalid Dispatcher.slug {attrs["slug"]}')

        cls = super().__new__(mcs, class_name, bases, attrs)
        if cls not in dispatcherManager:
            dispatcherManager.register(cls)
            # mcs._dispatchers.append(cls)
            # mcs._all[cls.slug] = mcs._all[int(cls.id)] = mcs._all[str(cls.id)] = cls
        return cast(Dispatcher, cls)


class Payload:
    message: str
    subject: str | None = None
    html_message: str | None = None
    event: "EventType"
    channel: "Channel"
    user: "User"

    def __init__(
        self,
        message: str,
        event: "EventType",
        channel: "Channel",
        user: "User",
        subject: str = "",
        html_message: str = "",
        **kwargs: Dict[str, Any],
    ):
        self.message = message
        self.event = event
        self.channel = channel
        self.subject = subject
        self.html_message = html_message
        self.user = user
        for k, v in kwargs.items():
            setattr(self, k, v)

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__


class Config(forms.Form):
    pass


class Dispatcher(metaclass=DispatcherMeta):
    id = -1
    slug = "--"
    local = True
    verbose_name: str = ""
    text_message: bool = True
    html_message: bool = False
    config_class: Type[Config] = Config
    config: Dict[str, Any] = {}
    channel: "Channel"

    def __init__(self, channel: "Channel") -> None:
        self.channel = channel

    def send(self, address: str, payload: Payload) -> None: ...

    @classproperty
    def name(cls) -> str:
        return cls.verbose_name or cls.__name__.title()


class DispatcherManager(Registry):
    pass


dispatcherManager = DispatcherManager(Dispatcher)
