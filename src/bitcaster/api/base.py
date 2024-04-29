from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import views, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

from .permissions import (
    ApiApplicationPermission,
    ApiKeyAuthentication,
    ApiOrgPermission,
    ApiProjectPermission,
)


class SecurityMixin:
    authentication_classes = (BasicAuthentication, SessionAuthentication, ApiKeyAuthentication)
    permission_classes = [ApiOrgPermission, ApiProjectPermission, ApiApplicationPermission]
    required_grants = []

    @property
    def grants(self):
        return self.required_grants


class BaseView(SecurityMixin, views.APIView):
    renderer_classes = (JSONRenderer,)


class BaseViewSet(SecurityMixin, viewsets.ViewSet):
    renderer_classes = (JSONRenderer,)


class BaseModelViewSet(SecurityMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_backends = [DjangoFilterBackend]
    serializer_classes = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)
