from typing import TypeVar

from django.http import HttpRequest, HttpResponseBase

from bitcaster.models import User

AnyRequest = TypeVar("AnyRequest", bound=HttpRequest, covariant=True)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponseBase, covariant=True)
# RedirectOrResponse = Union[HttpResponseRedirect, HttpResponseRedirectToReferrer, HttpResponse, StreamingHttpResponse]

class AuthHttpRequest(HttpRequest):
    user: User
