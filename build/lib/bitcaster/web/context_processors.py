from bitcaster import VERSION
from bitcaster.config import env
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def version(request: "HttpRequest") -> dict[str, dict[str, str]]:
    return {
        "bitcaster": {
            "version": VERSION,
            "doc_site": env("BITCASTER_DOCUMENTATION_SITE_URL"),
        }
    }
