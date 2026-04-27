from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
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


class ChannelView(SecurityMixin, ViewSet, ListAPIView[Channel], RetrieveAPIView[Channel]):
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
        return Channel.objects.none()

    @extend_schema(
        responses={200: ChannelSerializer(many=True)},
        description=_("List all notification channels (email, sms, etc.) configured for an organization."),
    )
    def list_for_org(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={200: ChannelSerializer(many=True)},
        description=_("List all notification channels available for a specific project."),
    )
    def list_for_project(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={200: ChannelSerializer}, description=_("Retrieve details of a specific notification channel.")
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)
