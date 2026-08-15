from typing import Callable

import re

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class CorsMiddleware:
    """Minimal CORS middleware for the public API.

    Mirrors the behaviour of django-cors-headers:

    - responses to requests carrying an ``Origin`` header that is listed in
      ``CORS_ALLOWED_ORIGINS`` get the ``Access-Control-Allow-Origin`` header;
    - preflight (OPTIONS with ``Access-Control-Request-Method``) requests are
      answered directly with the CORS headers when the origin is allowed, and
      with an empty 200 when it is not (the browser then blocks the request).
    """

    def __init__(self, get_response: "Callable[[HttpRequest], HttpResponse]") -> None:
        self.get_response = get_response
        self.url_regex = re.compile(settings.CORS_URLS_REGEX)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self.url_regex.match(request.path):
            origin = request.META.get("HTTP_ORIGIN")
            if origin:
                allowed = origin in settings.CORS_ALLOWED_ORIGINS
                if request.method == "OPTIONS" and request.META.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD"):
                    return self._preflight(allowed, origin)
                if allowed and request.method != "OPTIONS":
                    return self._add_headers(self.get_response(request), origin)
        return self.get_response(request)

    def _preflight(self, allowed: bool, origin: str) -> HttpResponse:
        if not allowed:
            return HttpResponse(status=200)
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = origin
        response["Vary"] = "Origin"
        response["Access-Control-Allow-Methods"] = ", ".join(settings.CORS_ALLOW_METHODS)
        response["Access-Control-Allow-Headers"] = ", ".join(settings.CORS_ALLOW_HEADERS)
        response["Access-Control-Max-Age"] = str(settings.CORS_PREFLIGHT_MAX_AGE)
        return response

    def _add_headers(self, response: HttpResponse, origin: str) -> HttpResponse:
        response["Access-Control-Allow-Origin"] = origin
        response["Vary"] = "Origin"
        if settings.CORS_ALLOW_CREDENTIALS:
            response["Access-Control-Allow-Credentials"] = "true"
        return response
