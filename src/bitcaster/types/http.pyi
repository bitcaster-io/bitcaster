from typing import Awaitable, Protocol, TypeVar, type_check_only

from rest_framework.request import Request
from user_agents.parsers import UserAgent

from django.contrib.auth import AbstractBaseUser, AnonymousUser
from django.http import HttpRequest, HttpResponseBase

from bitcaster.models import ApiKey, User

class ApiRequest(Request):
    user: User | AnonymousUser
    auth: ApiKey | None

AnyRequest_co = TypeVar("AnyRequest_co", bound=HttpRequest, covariant=True)
AnyResponse_co = TypeVar("AnyResponse_co", bound=HttpResponseBase, covariant=True)

class AuthHttpRequest(HttpRequest):
    user: AbstractBaseUser | AnonymousUser

class UserAgentRequest(HttpRequest):
    user_agent: UserAgent

@type_check_only
class GetResponseCallable(Protocol):
    def __call__(self, request: HttpRequest, /) -> HttpResponseBase: ...

@type_check_only
class AsyncGetResponseCallable(Protocol):
    def __call__(self, request: HttpRequest, /) -> Awaitable[HttpResponseBase]: ...
