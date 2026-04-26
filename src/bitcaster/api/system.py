from typing import TYPE_CHECKING, Any, cast

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from ..auth.constants import Grant
from .base import BaseView
from .permissions import ApiKeyAuthentication

if TYPE_CHECKING:
    from bitcaster.models import ApiKey


class PingSerializer(serializers.Serializer[Any]):
    token = serializers.CharField()


class PingView(BaseView):
    required_grants = [Grant.SYSTEM_PING]
    serializer_class = PingSerializer
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        request=PingSerializer,
        responses={200: PingSerializer},
        description=_("Check the system status and verify the validity of the API token."),
    )
    def get(self, request: Request, **kwargs: Any) -> Response:
        key: "ApiKey" = cast("ApiKey", request.auth)
        ser = PingSerializer({"token": key.name})
        return Response(ser.data, status=status.HTTP_200_OK)


class LoginView(BaseView):
    required_grants = [Grant.SYSTEM_PING]
    serializer_class = PingSerializer
    authentication_classes = [ApiKeyAuthentication]

    @extend_schema(
        request=PingSerializer,
        responses={200: PingSerializer},
        description=_("Endpoint for API authentication and verification."),
    )
    def get(self, request: Request, **kwargs: Any) -> Response:
        key: "ApiKey" = cast("ApiKey", request.auth)
        ser = PingSerializer({"token": key.name})
        return Response(ser.data, status=status.HTTP_200_OK)
