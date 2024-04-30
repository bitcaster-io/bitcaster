from typing import TYPE_CHECKING, Type

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import views, viewsets
from rest_framework.authentication import (
    BaseAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import BasePermission
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.serializers import Serializer

from ..auth.constants import Grant
from .permissions import (
    ApiApplicationPermission,
    ApiKeyAuthentication,
    ApiOrgPermission,
    ApiProjectPermission,
)

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


class SecurityMixin:
    authentication_classes: "_ListOrTuple[BaseAuthentication]" = (
        BasicAuthentication,
        SessionAuthentication,
        ApiKeyAuthentication,
    )
    permission_classes: "_ListOrTuple[BasePermission]" = (
        ApiOrgPermission,
        ApiProjectPermission,
        ApiApplicationPermission,
    )
    required_grants: "_ListOrTuple[Grant]" = ()

    @property
    def grants(self) -> "_ListOrTuple[Grant]":
        return self.required_grants


class BaseView(SecurityMixin, views.APIView):
    renderer_classes = (JSONRenderer,)


class BaseViewSet(SecurityMixin, viewsets.ViewSet):
    renderer_classes = (JSONRenderer,)


class BaseModelViewSet(SecurityMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_backends = [DjangoFilterBackend]
    serializer_classes = {}

    def get_serializer_class(self) -> Type[Serializer]:
        return self.serializer_classes.get(self.action, self.serializer_class)
