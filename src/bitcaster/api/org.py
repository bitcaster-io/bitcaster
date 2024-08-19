from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse
from google.protobuf.internal.well_known_types import Any
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ChannelSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import Organization
from bitcaster.utils.http import absolute_uri


class OrgSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("name", "slug", "users", "projects")

    def get_users(self, obj: Organization) -> str:
        return absolute_uri(reverse("api:user-list", kwargs={"org": obj.slug}))

    def get_projects(self, obj: Organization) -> str:
        return absolute_uri(reverse("api:project-list", kwargs={"org": obj.slug}))


class OrgView(SecurityMixin, ViewSet, RetrieveAPIView):
    """
    Organization details
    """

    serializer_class = OrgSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "org"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Organization]:
        return Organization.objects.exclude(id=Bitcaster.app.organization.pk)

    @action(detail=True, methods=["GET"], description="Channel list")
    def channels(self, request: HttpRequest, **kwargs: Any) -> Response:
        org: Organization = self.get_object()
        ser = ChannelSerializer(many=True, instance=org.channel_set.filter(project__isnull=True))
        return Response(ser.data)

    # @action(detail=True, methods=["GET"], description="Channel list")
    # def projects(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     org: Organization = self.get_object()
    #     ser = ProjectSerializer(many=True, instance=org.projects.filter())
    #     return Response(ser.data)
