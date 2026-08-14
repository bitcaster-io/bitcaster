from typing import TYPE_CHECKING

from rest_framework import views
from rest_framework.authentication import (
    BaseAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.migrations.serializer import BaseSerializer

from bitcaster.api.permissions import ApiApplicationPermission, ApiKeyAuthentication
from bitcaster.api.throttling import SlidingWindowThrottle
from bitcaster.exceptions import InvalidGrantError, InvalidOriginError

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission

    from django.utils.datastructures import _ListOrTuple

    from bitcaster.auth.constants import Grant


class SecurityMixin(APIView):
    authentication_classes: "_ListOrTuple[type[BaseAuthentication]]" = (
        ApiKeyAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    permission_classes: "_ListOrTuple[type[BasePermission]]" = (ApiApplicationPermission,)
    required_grants: "_ListOrTuple[Grant]" = ()
    throttle_classes = [SlidingWindowThrottle]

    @property
    def grants(self) -> "_ListOrTuple[Grant]":
        return self.required_grants

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, InvalidGrantError | InvalidOriginError):
            return Response({"detail": str(exc)}, status=403)
        return super().handle_exception(exc)

    def get_serializer_class(self) -> type[BaseSerializer]:
        if hasattr(self, "action_serializers"):
            return self.action_serializers.get(self.action, self.serializer_class)
        return super().get_serializer_class()


class SerializerMixin(APIView):
    pass


class BaseView(SecurityMixin, views.APIView):
    renderer_classes = (JSONRenderer,)
