from typing import TYPE_CHECKING, Any, Sequence
from urllib.parse import urljoin

from django.conf import settings
from django.http.request import split_domain_port
from django.urls import reverse

from ..state import state

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ..types.http import AnyRequest


def get_server_host(request: "AnyRequest | None" = None) -> str:
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


def absolute_reverse(name: str, args: Sequence[Any] | None = None, kwargs: dict[str, Any] | None = None) -> str:
    return absolute_uri(reverse(name, args=args, kwargs=kwargs))


def get_client_ip() -> str:
    # This uses the first item in X-Forwarded-For, It does not work on Heroku:
    # @see https://stackoverflow.com/questions/18264304/get-clients-real-ip-address-on-heroku#answer-18517550
    x_forwarded_for = state.request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    elif real := state.request.META.get("HTTP_X_REAL_IP"):
        ip = real
    else:
        ip = state.request.META.get("REMOTE_ADDR")
    return ip.strip()
