from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ApplicationSerializer, ProjectSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import Organization, Project
from bitcaster.utils.http import absolute_uri


class OrgSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("name", "slug", "users")

    def get_users(self, obj: Organization) -> str:
        return absolute_uri(reverse("api:user-list", kwargs={"org": obj.slug}))


class ProjectView(SecurityMixin, ViewSet, ListAPIView, RetrieveAPIView):
    """
    Project details
    """

    serializer_class = ProjectSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "prj"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.exclude(organization_id=Bitcaster.app.organization.pk).filter(
            organization__slug=self.kwargs["org"],
        )

    @action(detail=True, methods=["GET"], description="Channel list")
    def applications(self, request: HttpRequest, **kwargs: Any) -> Response:
        prj: Project = self.get_object()
        ser = ApplicationSerializer(many=True, instance=prj.applications.all())
        return Response(ser.data)

    #
    # @action(detail=True, methods=["GET"], description="Channel list")
    # def projects(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     org: Organization = self.get_object()
    #     ser = ProjectSerializer(many=True, instance=org.projects.filter())
    #     return Response(ser.data)
