import contextlib
import json
from copy import copy
from datetime import datetime, timedelta
from threading import local
from typing import TYPE_CHECKING, Any, Iterator, Mapping

if TYPE_CHECKING:
    from bitcaster.types.django import JsonType
    from bitcaster.types.http import AnyRequest, AnyResponse

not_set = object()


class State(local):
    request: "AnyRequest|None" = None
    cookies: dict[str, list[Any]] = {}

    def __repr__(self) -> str:
        return f"<State {id(self)}>"

    def add_cookie(
        self,
        key: str,
        value: "JsonType",
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

    def get_cookie(self, name: str) -> str | None:
        return self.request.COOKIES.get(name)

    def set_cookies(self, response: "AnyResponse") -> None:
        for name, args in self.cookies.items():
            response.set_cookie(name, *args)

    @contextlib.contextmanager
    def configure(self, **kwargs: Any) -> "Iterator[None]":
        pre = copy(self.__dict__)
        self.reset()
        with self.set(**kwargs):
            yield
        for k, v in pre.items():
            setattr(self, k, v)

    @contextlib.contextmanager
    def set(self, **kwargs: "Mapping[str,Any]") -> "Iterator[None]":
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
