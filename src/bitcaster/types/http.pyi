from typing import Awaitable, Protocol, TypeVar, type_check_only

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponseBase
from rest_framework.request import Request
from user_agents.parsers import UserAgent

from bitcaster.models import ApiKey, User

class ApiRequest(Request):
    user: AbstractBaseUser | AnonymousUser
    auth: ApiKey | None

AnyRequest = TypeVar("AnyRequest", bound=HttpRequest, covariant=True)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponseBase, covariant=True)

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
