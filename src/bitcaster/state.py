import contextlib
import json
from copy import copy
from datetime import datetime, timedelta
from functools import cached_property
from threading import local
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from bitcaster.constants import Bitcaster

if TYPE_CHECKING:
    from bitcaster.models import Application
    from bitcaster.types.http import AnyRequest, AnyResponse

not_set = object()


class State(local):
    request: "AnyRequest|None" = None
    cookies: Dict[str, List[Any]] = {}
    # app: "Application" = None

    def __repr__(self) -> str:
        return f"<State {id(self)} - {self.timestamp}>"

    def add_cookie(
        self,
        key: str,
        value: str,
        max_age: [int | float, timedelta] = None,
        expires: [str | datetime] = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str | None = None,
    ) -> None:
        value = json.dumps(value)
        self.cookies[key] = [value, max_age, expires, path, domain, secure, httponly, samesite]

    @cached_property
    def app(self) -> "Application":
        from bitcaster.models import Application

        return Application.objects.get(
            name=Bitcaster.APPLICATION,
            project__name=Bitcaster.PROJECT,
            project__organization__name=Bitcaster.ORGANIZATION,
        )

    def get_cookie(self, name: str) -> Optional[str]:
        return self.request.COOKIES.get(name)

    def set_cookies(self, response: "AnyResponse") -> None:
        for name, args in self.cookies.items():
            response.set_cookie(name, *args)

    @contextlib.contextmanager
    def configure(self, **kwargs: "Dict[str,Any]") -> "Iterator[None]":
        pre = copy(self.__dict__)
        self.reset()
        with self.set(**kwargs):
            yield
        for k, v in pre.items():
            setattr(self, k, v)

    @contextlib.contextmanager
    def set(self, **kwargs: "Dict[str,Any]") -> "Iterator[None]":
        pre = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                pre[k] = getattr(self, k)
            else:
                pre[k] = not_set
            setattr(self, k, v)
        yield
        for k, v in pre.items():
            if v is not_set:
                delattr(self, k)
            else:
                setattr(self, k, v)

    def reset(self) -> None:
        self.request = None
        self.cookies = {}


state = State()
