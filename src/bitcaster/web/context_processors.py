from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.template.context_processors import debug as django_debug

from bitcaster import VERSION

if TYPE_CHECKING:
    from django.http import HttpRequest


def version(request: "HttpRequest") -> dict[str, dict[str, str]]:
    return {
        "bitcaster": {
            "version": VERSION,
            "doc_site": settings.BITCASTER_DOCUMENTATION_SITE_URL,
        }
    }


def debug(request: "HttpRequest") -> dict[str, Any]:
    return django_debug(request)
