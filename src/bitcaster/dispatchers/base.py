import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, cast

from django.core.exceptions import ValidationError
from django.forms import forms
from django.utils.functional import cached_property, classproperty
from jinja2.utils import import_string
from strategy_field.registry import Registry

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, User
    from bitcaster.types.dispatcher import DispatcherHandler, TDispatcherConfig

logger = logging.getLogger(__name__)


class DispatcherMeta(type["Dispatcher"]):
    _all = {}
    _dispatchers = []

    def __new__(mcs: Type["Dispatcher"], class_name: str, bases: Tuple[Any], attrs: Dict[str, Any]) -> "Dispatcher":
        if attrs["__qualname__"] == "Dispatcher":
            return super().__new__(mcs, class_name, bases, attrs)

        if attrs["slug"].isnumeric():  # pragma: no cache
            raise ValueError(f'{class_name} Invalid Dispatcher.slug {attrs["slug"]}')
        if attrs["slug"] in mcs._all:  # pragma: no cache
            raise ValueError(f'{class_name} Duplicate Dispatcher.slug {attrs["slug"]}')

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
    text_message: bool = True
    html_message: bool = False
    has_subject: bool = False
    config_class: "Type[DispatcherConfig]" = DispatcherConfig
    backend: "Optional[str, DispatcherHandler]" = None

    channel: "Channel"

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

    def send(self, address: str, payload: Payload) -> None: ...

    @classproperty
    def name(cls) -> str:
        return cls.verbose_name or cls.__name__.title()


class DispatcherManager(Registry):
    pass


dispatcherManager = DispatcherManager(Dispatcher)
