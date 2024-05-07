from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple


class SecurityMixin(APIView):
    authentication_classes: "_ListOrTuple[BaseAuthentication]" = (
        BasicAuthentication,
        SessionAuthentication,
        ApiKeyAuthentication,
    )
    permission_classes: "_ListOrTuple[BasePermission]" = (
        # ApiOrgPermission,
        # ApiProjectPermission,
        ApiApplicationPermission,
    )
    required_grants: "_ListOrTuple[Grant]" = ()

    @property
    def grants(self) -> "_ListOrTuple[Grant]":
        return self.required_grants


class BaseView(SecurityMixin, views.APIView):
    renderer_classes = (JSONRenderer,)


#
# class BaseViewSet(SecurityMixin, viewsets.ViewSet):
#     renderer_classes = (JSONRenderer,)
#
#
# class BaseModelViewSet(SecurityMixin, viewsets.ReadOnlyModelViewSet):
#     renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
#     filter_backends = [DjangoFilterBackend]
#     serializer_classes = {}
#
#     def get_serializer_class(self) -> Type[Serializer]:
#         return self.serializer_classes.get(self.action, self.serializer_class)
