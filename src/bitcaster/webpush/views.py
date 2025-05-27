import json
import logging
from typing import TYPE_CHECKING, Any

from django import forms
from django.conf import settings
from django.forms import Media
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    JsonResponse,
)
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView, TemplateView, View

import bitcaster
from bitcaster.models import Application, Assignment, Channel

from .utils import unsign

if TYPE_CHECKING:
    from bitcaster.webpush.utils import SignatureT

logger = logging.getLogger(__name__)


class SecretMixin(View):
    def unsign(self) -> Assignment:
        secret = self.kwargs["secret"]
        data: "SignatureT" = unsign(secret)
        try:
            return Assignment.objects.select_related("channel").get(pk=data["pk"], address__value=data["address"])
        except Assignment.DoesNotExist:
            raise Http404  # noqa: B904


class DataView(SecretMixin, RedirectView):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        secret = self.kwargs["secret"]
        assignment: Assignment = self.unsign()
        ch: Channel = assignment.channel
        return JsonResponse(
            {
                "k": ch.config["APPLICATION_SERVER_KEY"],
                "s": reverse("webpush:subscribe", args=[secret]),
                "u": reverse("webpush:unsubscribe", args=[secret]),
                "w": reverse("webpush:service_worker", args=[assignment.channel.project.slug]),
            }
        )


class UnSubscribeView(SecretMixin, RedirectView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        assignment: Assignment = self.unsign()
        assignment.data = {"status": "denied"}
        assignment.validated = False
        assignment.save()
        return JsonResponse({"error": "Unsubscribed"}, status=200)


class SubscribeView(SecretMixin, RedirectView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        assignment: Assignment = self.unsign()
        assignment.data = {"webpush": json.loads(request.body)}
        assignment.validated = True
        assignment.save()
        return JsonResponse({"error": "Subscription created"}, status=201)


class ConfirmView(SecretMixin, TemplateView):
    template_name = "push/ask.html"

    @property
    def media(self) -> forms.Media:
        extra = "" if settings.DEBUG else ".min"
        js = [
            "webpush/axios%s.js" % extra,
            "webpush/jquery-3.7.1%s.js" % extra,
            "webpush/js.cookie%s.js" % extra,
            "webpush/webpush-client%s.js" % extra,
            "webpush/knockout-3.5.1%s.js" % extra,
        ]
        return Media(js=js)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        secret = self.kwargs["secret"]
        assignment = self.unsign()
        ch: "Channel" = assignment.channel

        return {
            "assignment": assignment,
            "owner": assignment.channel.owner,
            "secret": secret,
            "private_key": ch.config["APPLICATION_SERVER_KEY"],
            "subscribe_url": reverse("webpush:subscribe", args=[secret]),
            "unsubscribe_url": reverse("webpush:unsubscribe", args=[secret]),
            "media": self.media,
            "sw": reverse("webpush:service_worker", args=[assignment.channel.project.slug]),
        }


class ServiceWorker(TemplateView):
    template_name = "push/serviceworker%s.js"
    content_type = "application/javascript"

    def get_template_names(self) -> list[str]:
        extra = ".min" if settings.DEBUG else ""
        return [self.template_name % extra]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["version"] = bitcaster.VERSION
        kwargs["application"] = Application.objects.get(slug=self.kwargs["application"])
        return super().get_context_data(**kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        response_kwargs["headers"] = {"Service-Worker-Allowed": "/"}
        return super().render_to_response(context, **response_kwargs)
