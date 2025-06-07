from typing import TYPE_CHECKING, Awaitable

from django.http import HttpResponseBase
from django.utils.functional import SimpleLazyObject

from bitcaster.utils.user_agent import get_user_agent

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from bitcaster.types.http import AsyncGetResponseCallable, GetResponseCallable


class UserAgentMiddleware:
    def __init__(self, get_response: "GetResponseCallable | AsyncGetResponseCallable") -> None:
        self.get_response = get_response

    def __call__(self, request: "WSGIRequest") -> HttpResponseBase | Awaitable[HttpResponseBase]:
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))
        return self.get_response(request)
