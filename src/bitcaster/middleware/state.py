import logging

from bitcaster.state import state
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from bitcaster.types.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class StateMiddleware:
    """Middleware that puts the request object in thread local storage."""

    def __init__(self, get_response: [Callable] = None) -> None:
        self.get_response = get_response

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        state.request = request
        response = self.get_response(request)
        state.set_cookies(response)
        state.request = None
        state.cookies = {}
        return response
