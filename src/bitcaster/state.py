import contextlib
import json
from copy import copy
from datetime import datetime, timedelta
from threading import local
from typing import TYPE_CHECKING, Any, Dict, Iterator, List

if TYPE_CHECKING:
    from bitcaster.types.http import AnyRequest, AnyResponse

not_set = object()


class State(local):
    request: "AnyRequest|None" = None
    cookies: Dict[str, List[Any]] = {}

    def __repr__(self) -> str:
        return f"<State {id(self)} - {self.timestamp}>"

    def add_cookies(
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
