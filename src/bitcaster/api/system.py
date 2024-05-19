from typing import TYPE_CHECKING, Any

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from ..auth.constants import Grant
from .base import BaseView

if TYPE_CHECKING:
    from bitcaster.models import ApiKey


class PingSerializer(serializers.Serializer):
    token = serializers.CharField()


class PingView(BaseView):
    required_grants = [Grant.SYSTEM_PING]
    serializer_class = PingSerializer
    # authentication_classes = [ApiKeyAuthentication]
    # permission_classes = []

    def get(self, request: Request, **kwargs: Any) -> Response:
        key: "ApiKey" = request.auth
        ser = PingSerializer({"token": key.name})
        return Response(ser.data, status=status.HTTP_200_OK)
