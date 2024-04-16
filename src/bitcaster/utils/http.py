from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.http.request import split_domain_port
from django.urls import reverse

from ..state import state

if TYPE_CHECKING:
    from ..types.http import AnyRequest


class HttpResponseRedirectToReferrer(HttpResponseRedirect):
    def __init__(self, request: "AnyRequest", *args: Any, **kwargs: Any):
        redirect_to = request.META.get("HTTP_REFERER", "/")
        super().__init__(redirect_to, *args, **kwargs)


def get_server_host(request: "Optional[AnyRequest]" = None) -> str:
    req: HttpRequest | None = request or state.request
    host = req.get_host()
    domain, port = split_domain_port(host)
    return domain


def get_server_url() -> str:
    req: HttpRequest | None = state.request
    host = ""
    if req:
        host = req.build_absolute_uri("/")[:-1]
        if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS:
            host = host.replace("http://", "https://")
    return host


def absolute_uri(url: str | None = None) -> str:
    req: "HttpRequest|None" = state.request
    if req:
        uri = req.build_absolute_uri(url)
    elif not url:
        uri = get_server_url()
    else:
        uri = urljoin(get_server_url().rstrip("/") + "/", url.lstrip("/"))
    if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS:
        uri = uri.replace("http://", "https://")
    return uri


def absolute_reverse(name: str, args: Tuple[Any] | None = None, kwargs: Dict[str, Any] | None = None) -> str:
    return absolute_uri(reverse(name, args=args, kwargs=kwargs))
