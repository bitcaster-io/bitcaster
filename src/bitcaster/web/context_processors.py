from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.template.context_processors import debug as django_debug

from bitcaster import VERSION
from bitcaster.config import env
from bitcaster.utils.http import get_client_ip

if TYPE_CHECKING:
    from django.http import HttpRequest


def version(request: "HttpRequest") -> dict[str, dict[str, str]]:
    return {
        "bitcaster": {
            "version": VERSION,
            "doc_site": env("BITCASTER_DOCUMENTATION_SITE_URL"),
        }
    }


def debug(request: "HttpRequest") -> dict[str, Any]:
    return django_debug(request)


def get_suffix(request: "HttpRequest")->str:
    if settings.PWA_APP_SUFFIX:
        return settings.PWA_APP_SUFFIX
    env = get_environment(request)
    if env == "dev":
        return "[dev]"
    elif env == "staging":
        return "[qa]"
    return ""



def get_environment(request: "HttpRequest") -> str:
    host = request.get_host()
    ip = get_client_ip(request)
    if ip == "127.0.0.1":
        return "local"
    if host.startswith("localhost"):
        return "local"
    else:
        name = host.split(".", maxsplit=1)[0]
        if name in ["dev"]:
            return "dev"
        elif name in ["qa"]:
            return "staging"
        elif name in ["app", "sosbob", "bob"]:
            return "prod"
    return "unknown"
