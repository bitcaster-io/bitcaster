from typing import Optional, TypeVar

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponseBase, HttpResponseRedirect
from rest_framework.request import Request

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
