from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework import views
from rest_framework.authentication import (
    BaseAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from ..auth.constants import Grant
from .permissions import ApiApplicationPermission, ApiKeyAuthentication
from ..exceptions import InvalidGrantError

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


class SecurityMixin(APIView):
    authentication_classes: "_ListOrTuple[BaseAuthentication]" = (
        ApiKeyAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    permission_classes: "_ListOrTuple[BasePermission]" = (ApiApplicationPermission,)
    required_grants: "_ListOrTuple[Grant]" = ()

    @property
    def grants(self) -> "_ListOrTuple[Grant]":
        return self.required_grants

    def handle_exception(self, exc):
        if isinstance(exc, (InvalidGrantError,)):
            response = Response({'detail': str(exc)}, status=403)
            return response

        return super().handle_exception(exc)


class BaseView(SecurityMixin, views.APIView):
    renderer_classes = (JSONRenderer,)
