import json
from datetime import timedelta, datetime
from threading import local
from typing import Dict, List, Any

from django.http import HttpResponse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.types.http import AnyRequest, AnyResponse


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


state = State()
