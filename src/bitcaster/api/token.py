from typing import TYPE_CHECKING, Any

from datetime import timedelta
from urllib.parse import urlsplit

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import SecurityMixin
from .permissions import ApiKeyAuthentication
from ..auth.constants import Grant
from ..exceptions import InvalidGrantError
from ..models import ApiKey, Application, ClientToken, Event
from ..models.key import ApiKeyKind

if TYPE_CHECKING:
    from rest_framework.request import Request


class ClientTokenSerializer(serializers.Serializer[Any]):
    event = serializers.CharField(required=False, allow_null=True, max_length=255)
    origin = serializers.CharField()

    def validate_origin(self, value: str) -> str:
        parts = urlsplit(value)
        if parts.scheme not in ("http", "https") or not parts.netloc or parts.path or parts.query or parts.fragment:
            raise serializers.ValidationError(_("origin must be an http(s) origin without path or query"))
        return f"{parts.scheme}://{parts.netloc}"


class ClientTokenView(SecurityMixin, GenericAPIView[Application]):
    """Mint a short-lived client token to be used from web pages."""

    serializer_class = ClientTokenSerializer
    required_grants = [Grant.EVENT_TRIGGER, Grant.WEB_TRIGGER]
    authentication_classes = [ApiKeyAuthentication]
    http_method_names = ["post"]
    throttle_rate = 20
    throttle_window = 60

    def get_queryset(self) -> "Any":
        return Application.objects.select_related("project__organization").filter(
            project__organization__slug=self.kwargs["org"],
            project__slug=self.kwargs["prj"],
            slug=self.kwargs["app"],
        )

    @extend_schema(
        request=ClientTokenSerializer,
        responses={201: Any},
        description=_(
            "Mint a short-lived client token scoped to this application. "
            "Client tokens can only trigger events and expire after a short period of time. "
            "Only server API keys can use this endpoint."
        ),
    )
    def post(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        parent = request.auth
        if not isinstance(parent, ApiKey) or parent.kind == ApiKeyKind.WEB:
            raise InvalidGrantError("Client tokens can only be minted with server API keys")

        ser = ClientTokenSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        application = self.get_queryset().first()
        if not application:
            return Response({"error": f"Application not found {self.kwargs}"}, status=status.HTTP_404_NOT_FOUND)

        event: Event | None = None
        if event_slug := ser.validated_data.get("event"):
            try:
                event = Event.objects.get(application=application, slug=event_slug)
            except Event.DoesNotExist:
                return Response({"error": f"Event not found {self.kwargs}"}, status=status.HTTP_404_NOT_FOUND)

        ClientToken.objects.filter(expires_at__lte=timezone.now()).delete()

        token = ClientToken.objects.create(
            user=parent.user,
            parent=parent,
            organization=application.project.organization,
            project=application.project,
            application=application,
            event=event,
            environments=parent.environments or None,
            allowed_origins=[ser.validated_data["origin"]],
            expires_at=timezone.now() + timedelta(seconds=settings.CLIENT_TOKEN_TTL),
        )
        data: dict[str, Any] = {
            "token": token.token,
            "expires_at": token.expires_at,
            "event": event.slug if event else None,
        }
        return Response(data, status=status.HTTP_201_CREATED)
