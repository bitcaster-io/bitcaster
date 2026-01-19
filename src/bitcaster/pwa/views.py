import json
import logging
import secrets
from enum import IntEnum, unique
from typing import TYPE_CHECKING, Any

import httpagentparser
from django.conf import settings
from django.db.transaction import atomic
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from bitcaster.pwa import app_settings
from bitcaster.utils.http import get_server_url, absolute_reverse
from bitcaster.web.context_processors import get_suffix
from bitcaster.webpush.views import SubscribeView

# from ..dispatchers import MobileApp
# from ..exceptions import CaseAlreadyOpen, UsageLimit
# from ..models import Assignment, Person, Sender
# from ..utils.http import absolute_reverse, get_server_url
# from ..utils.qr import get_qrcode
# from ..utils.throttling import get_address_usage
# from ..validators import is_valid_location
# from ..web.context_processors import get_environment, get_suffix
# from . import app_settings
# from ..webpush.views import SubscribeView

if TYPE_CHECKING:
    from typing import Optional

logger = logging.getLogger(__name__)


@unique
class Codes(IntEnum):
    SUCCESS = 200
    INTERNAL_ERROR = 500
    INVALID_CODE = 104

    WRONG_PAYLOAD = 400
    MISSING_TOKEN = 401
    INVALID_TOKEN = 402
    TOKEN_MISMATCH = 403
    INVALID_DEVICE = 404


# @method_decorator(csrf_exempt, name="dispatch")
class MobileRegisterView(SubscribeView):
    pass
    # def post(self, request, *args, **kwargs):
    #     from bitcaster.webpush.views import SubscribeView
    #
    #     return SubscribeView.as_view().dispatch(request)


@method_decorator(csrf_exempt, name="dispatch")
class MobileView(TemplateView):
    template_name = "pwa/index.html"
    request: "HttpRequest"


class PwaServiceWorker(TemplateView):
    content_type = "application/javascript"
    template_name = "pwa/serviceworker.js"

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        kwargs.update(
            {
                "urls": json.dumps(["favicon.ico", static("bob/images/bob_error.svg")]),
                # "apiKey": settings.FIREBASE_CONFIG["apiKey"],
                # "projectId": settings.FIREBASE_CONFIG["projectId"],
                # "appId": settings.FIREBASE_CONFIG["appId"],
                # "messagingSenderId": settings.FIREBASE_CONFIG["messagingSenderId"],
            }
        )

        return super().get_context_data(**kwargs)

    @method_decorator(never_cache)
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        # context["urls"] = json.dumps(["favicon.ico", static("bob/images/bob_error.svg")])
        response_kwargs["headers"] = {"Service-Worker-Allowed": "/"}
        return super().render_to_response(context, **response_kwargs)


@never_cache
def manifest(request: HttpRequest, secret: str) -> HttpResponse:
    return render(
        request,
        "pwa/manifest.json",
        {
            "host": get_server_url(),
            "suffix": get_suffix(request),
            "start_url": absolute_reverse("pwa-home", args=[secret]),
            "home": absolute_reverse("pwa-home", args=[secret]),
            "secret": secret,
            "manifest": absolute_reverse("pwa-manifest", args=[secret]),
            **{
                setting_name: getattr(app_settings, setting_name)
                for setting_name in dir(app_settings)
                if setting_name.startswith("PWA_")
            },
        },
        content_type="application/json",
    )


def offline(request: HttpRequest) -> HttpResponse:
    return render(request, "pwa/offline.html")
