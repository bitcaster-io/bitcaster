from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ApplicationSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import bitcaster
from bitcaster.models import Application


class ApplicationView(SecurityMixin, ViewSet, RetrieveAPIView[Application], ListAPIView[Application]):
    """List Project applications."""

    serializer_class = ApplicationSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "app"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Application]:
        return Application.objects.exclude(project__organization_id=bitcaster.app.organization.pk).filter(
            project__organization__slug=self.kwargs["org"],
            project__slug=self.kwargs["prj"],
        )

    @extend_schema(
        responses={200: ApplicationSerializer(many=True)},
        description=_("List all applications within a specific project."),
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={200: ApplicationSerializer},
        description=_("Retrieve detailed information about a specific application using its slug."),
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)
