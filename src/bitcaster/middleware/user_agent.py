from typing import TYPE_CHECKING, Callable

from django.utils.functional import SimpleLazyObject

from bitcaster.utils.user_agent import get_user_agent

if TYPE_CHECKING:
    from bitcaster.types.http import AnyRequest, AnyResponse


class UserAgentMiddleware(object):
    def __init__(self, get_response: [Callable] = None) -> None:
        self.get_response = get_response

    def __call__(self, request: "AnyRequest") -> "AnyResponse":
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))
        return self.get_response(request)
