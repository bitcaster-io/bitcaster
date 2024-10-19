from typing import Awaitable, Optional, Protocol, TypeVar, type_check_only

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponseBase, HttpResponseRedirect
from rest_framework.request import Request
from user_agents.parsers import UserAgent

from bitcaster.models import ApiKey, User

class ApiRequest(Request):
    user: Optional[User]
    auth: Optional[ApiKey]

# ApiRequest = TypeVar("ApiRequest", bound=Request, covariant=True)
AnyRequest = TypeVar("AnyRequest", bound=HttpRequest, covariant=True)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponseBase, covariant=True)
# RedirectOrResponse = Union[HttpResponseRedirect, HttpResponseRedirectToReferrer, HttpResponse, StreamingHttpResponse]

class AuthHttpRequest(HttpRequest):
    user: User

class UserAgentRequest(HttpRequest):
    user_agent: UserAgent

@type_check_only
class GetResponseCallable(Protocol):
    def __call__(self, request: HttpRequest, /) -> HttpResponseBase: ...

@type_check_only
class AsyncGetResponseCallable(Protocol):
    def __call__(self, request: HttpRequest, /) -> Awaitable[HttpResponseBase]: ...
