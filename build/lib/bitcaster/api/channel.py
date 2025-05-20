from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ..auth.constants import Grant
from ..models import Channel
from .base import SecurityMixin
from .serializers import ChannelSerializer

app_name = "api"


class ChannelView(SecurityMixin, ViewSet, ListAPIView, RetrieveAPIView):
    """List channels."""

    serializer_class = ChannelSerializer
    required_grants = [Grant.ORGANIZATION_READ]

    def get_queryset(self) -> QuerySet[Channel]:
        if "prj" in self.kwargs:
            return Channel.objects.filter(
                organization__slug=self.kwargs["org"],
                project__slug=self.kwargs["prj"],
            )
        if "org" in self.kwargs:
            return Channel.objects.filter(
                organization__slug=self.kwargs["org"],
            )
        return None

    @extend_schema(description=_("List organization channels"))
    def list_for_org(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(description=_("List Project channels"))
    def list_for_project(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
