from typing import TYPE_CHECKING, Callable

from django.shortcuts import render
from social_core.exceptions import AuthException

if TYPE_CHECKING:  # pragma: no branch
    from bitcaster.types.http import HttpRequest, HttpResponse


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest], HttpResponse]|None" = None) -> None:
        self.get_response = get_response

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        return self.get_response(request)

    def process_exception(self, request: "HttpRequest", exception: Exception) -> "HttpResponse | None":
        if isinstance(exception, AuthException):
            return render(
                request,
                "bitcaster/errors/500.html",
                {"message": exception.__class__.__name__, "description": exception.__doc__, "code": 500},
                status=500,
            )
        return None
