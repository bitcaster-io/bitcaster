from typing import TYPE_CHECKING, Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from ..auth.constants import Grant
from .base import BaseView

if TYPE_CHECKING:
    from bitcaster.models import ApiKey


class PingView(BaseView):
    required_grants = [Grant.SYSTEM_PING]

    def get(self, request: Request, **kwargs: Any) -> Response:
        key: "ApiKey" = request.auth
        return Response({"token": key.name, "slug": key.application.slug}, status=status.HTTP_200_OK)
