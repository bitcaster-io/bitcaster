from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:  # pragma: no branch
    from bitcaster.types.http import HttpRequest, HttpResponse


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest], HttpResponse]|None" = None) -> None:
        self.get_response = get_response

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        return self.get_response(request)
