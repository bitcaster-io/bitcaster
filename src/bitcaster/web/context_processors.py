from django.http import HttpRequest

from bitcaster import VERSION
from bitcaster.config import env


def version(request: "HttpRequest") -> dict[str, dict[str, str]]:
    return {
        "bitcaster": {
            "version": VERSION,
            "doc_site": env("BITCASTER_DOCUMENTATION_SITE_URL"),
        }
    }
