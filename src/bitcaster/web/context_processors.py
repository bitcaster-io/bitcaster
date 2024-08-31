from django.http import HttpRequest

from bitcaster import VERSION


def version(request: "HttpRequest") -> dict[str, dict[str, str]]:
    return {"bitcaster": {"version": VERSION}}
