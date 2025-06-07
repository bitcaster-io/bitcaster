from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ProjectSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import bitcaster
from bitcaster.models import Project


class ProjectView(SecurityMixin, ViewSet, ListAPIView, RetrieveAPIView):
    """List Organization's projects."""

    serializer_class = ProjectSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "prj"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.exclude(organization_id=bitcaster.app.organization.pk).filter(
            organization__slug=self.kwargs["org"],
        )

    @extend_schema(description=_("Retrieve project details"))
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)
