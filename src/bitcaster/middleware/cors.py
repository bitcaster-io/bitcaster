from typing import TYPE_CHECKING

from django.http import HttpResponse, JsonResponse

from bitcaster.models import ApiKey
from bitcaster.models.key import KeyKind

if TYPE_CHECKING:
    from typing import Callable

    from django.http import HttpRequest, HttpResponseBase

ALLOWED_METHODS = ("POST", "OPTIONS")
ALLOWED_HEADERS = ("authorization", "content-type")


class BrowserCorsMiddleware:
    """CORS handling for PUBLIC API keys.

    Public keys are bound to an allowlist of origins and are meant to be used
    from browser clients. This middleware:

    - answers ``OPTIONS`` preflight requests for ``/api/`` paths carrying a
      valid PUBLIC key whose ``Origin`` is allowed
    - rejects actual cross-origin ``/api/`` requests whose ``Origin`` is not
      declared on the key
    - attaches the ``Access-Control-Allow-Origin`` header to allowed responses
    """

    def __init__(self, get_response: "Callable[[HttpRequest], HttpResponseBase]") -> None:
        self.get_response = get_response

    def __call__(self, request: "HttpRequest") -> "HttpResponseBase":
        if not request.path.startswith("/api/") or not request.META.get("HTTP_AUTHORIZATION"):
            return self.get_response(request)

        token = request.META["HTTP_AUTHORIZATION"].removeprefix("Key ").strip()
        key = ApiKey.objects.filter(kind=KeyKind.PUBLIC, key=token).first()
        if key is None:
            return self.get_response(request)

        origin = request.headers.get("Origin", "")
        if not origin or origin not in (key.origins or []):
            return JsonResponse({"detail": "Origin not allowed for this key"}, status=403)

        if request.method == "OPTIONS":
            response: "HttpResponseBase" = HttpResponse(status=200)
        else:
            response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
        response["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
        response["Vary"] = "Origin"
        return response
