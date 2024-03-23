import logging
from typing import TYPE_CHECKING, TypeVar, Optional, NotRequired, cast, Type, Tuple, Dict, Any

from django.utils.functional import classproperty

from bitcaster.utils.http import get_server_url

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    Payload = TypedDict("Payload", {"message": str, "subject": NotRequired[str]})

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
        if cls not in mcs._dispatchers:
            mcs._dispatchers.append(cls)
            mcs._all[cls.slug] = mcs._all[int(cls.id)] = mcs._all[str(cls.id)] = cls
        return cast(Dispatcher, cls)


class Dispatcher(metaclass=DispatcherMeta):
    id = -1
    slug = "--"
    local = True
    verbose_name = None
    text_message = True
    html = False

    @classmethod
    def send_message(cls, address: str, payload: Payload) -> None: ...

    @classproperty
    def name(cls) -> str:
        return cls.verbose_name or cls.__name__.title()


class DispatcherManager:
    def all(self) -> [Dispatcher]:
        for ch in DispatcherMeta._dispatchers:
            yield ch

    def slugs(self) -> [Dispatcher]:
        return [ch.slug for ch in self.all()]

    def get(self, id_or_name: str) -> Dispatcher:
        try:
            return DispatcherMeta._all[id_or_name]
        except KeyError:
            raise KeyError(f"Unknown dispatcher {id_or_name}")


dispatcherManager = DispatcherManager()
