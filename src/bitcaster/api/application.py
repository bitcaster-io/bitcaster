from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ApplicationSerializer, ProjectSerializer, EventSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import Organization, Project, Application
from bitcaster.utils.http import absolute_uri

#
# class OrgSerializer(serializers.ModelSerializer):
#     users = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Organization
#         fields = ("name", "slug", "users")
#
#     def get_users(self, obj: Organization) -> str:
#         return absolute_uri(reverse("api:user-list", kwargs={"org": obj.slug}))
#

class ApplicationView(SecurityMixin, ViewSet, RetrieveAPIView):
    """
    Application details
    """

    serializer_class = ProjectSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "app"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Organization]:
        return Application.objects.exclude(project__organization_id=Bitcaster.app.organization.pk).filter(
            project__organization__slug=self.kwargs["org"],
            project__slug=self.kwargs["prj"],
        )

    @action(detail=True, methods=["GET"], description="Events list", __doc__="aaaaaaa")
    def events(self, request: HttpRequest, **kwargs: Any) -> Response:
        app: Application = self.get_object()
        ser = EventSerializer(many=True, instance=app.events.all())
        return Response(ser.data)

    # @action(detail=True, methods=["GET"], description="Channel list")
    # def projects(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     org: Organization = self.get_object()
    #     ser = ProjectSerializer(many=True, instance=org.projects.filter())
    #     return Response(ser.data)
