from typing import Any

import json

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from .base import SecurityMixin
from ..auth.constants import Grant
from ..models import Assignment, DistributionList, Project
from ..utils.http import absolute_reverse


class DistributionAddSerializer(serializers.Serializer[DistributionList]):
    address = serializers.CharField()


class DistributionMemberSerializer(serializers.ModelSerializer[Assignment]):
    address = serializers.CharField(read_only=True, source="address.value")
    user = serializers.CharField(read_only=True, source="address.user.username")
    channel = serializers.CharField(read_only=True, source="channel.name")

    class Meta:
        model = Assignment
        fields = ("id", "address", "user", "channel", "active")


class DistributionListSerializer(serializers.ModelSerializer[DistributionList]):
    members = serializers.SerializerMethodField()

    class Meta:
        model = DistributionList
        fields = ("name", "id", "members", "application")

    def get_members(self, obj: Project) -> str:
        return absolute_reverse("api:members-list", args=[obj.project.organization.slug, obj.project.slug, obj.id])

    def validate_name(self, value: str) -> str:
        view: DistributionView = self.context["view"]
        if DistributionList.objects.filter(name__exact=value, project=view.project).exists():
            raise serializers.ValidationError("Name already exists!")
        return value

    def create(self, validated_data: dict[str, Any]) -> DistributionList:
        validated_data["project"] = self.context["view"].project
        return super().create(validated_data)


class DistributionView(
    SecurityMixin,
    ViewSet,
    ListAPIView[DistributionList],
    CreateAPIView[DistributionList],
    RetrieveAPIView[DistributionList],
):
    """List Project's DistributionList."""

    serializer_class = DistributionListSerializer
    required_grants = [Grant.DISTRIBUTION_LIST]

    @property
    def project(self) -> "Project":
        return Project.objects.select_related("organization").get(
            organization__slug=self.kwargs["org"], slug=self.kwargs["prj"]
        )

    def get_object(self) -> DistributionList:
        return self.project.distributionlist_set.get(pk=self.kwargs["pk"])

    def get_queryset(self) -> QuerySet[DistributionList]:
        return DistributionList.objects.filter(
            project__organization__slug=self.kwargs["org"], project__slug=self.kwargs["prj"]
        )

    @extend_schema(
        responses={200: DistributionListSerializer(many=True)},
        description=_("List all distribution lists within a specific project."),
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=DistributionListSerializer,
        responses={201: DistributionListSerializer},
        description=_("Create a new distribution list for the project."),
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={200: DistributionListSerializer}, description=_("Retrieve details of a specific distribution list.")
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description=_(
            "Add recipients to a DistributionList by providing a list of their address values (e.g., emails)."
        ),
        examples=[
            OpenApiExample(
                "Add users",
                description="Add users to a DistributionList adding any of his addresses",
                value=["user1@example.com", "user2@example.com"],
            ),
        ],
    )
    @action(detail=True, methods=["POST"])
    def add_recipient(self, request: Request, **kwargs: Any) -> Response:
        dl: DistributionList = self.get_object()
        try:
            data = json.loads(request.body)
            asms = Assignment.objects.filter(address__value__in=data)
            expected = len(data)
            found = len(asms)
            if found != expected:
                raise serializers.ValidationError("Invalid addresses")
            dl.recipients.add(*asms)
            return Response(
                {
                    "message": data,
                    "expected": expected,
                    "found": found,
                    "added": asms.values_list("address__value", flat=True),
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DistributionMembersView(SecurityMixin, ViewSet, ListAPIView[Assignment]):
    """Distribution list."""

    serializer_class = DistributionMemberSerializer
    required_grants = [Grant.DISTRIBUTION_LIST]

    def get_queryset(self) -> QuerySet[Assignment]:
        return Assignment.objects.filter(
            distributionlist__id=self.kwargs["pk"], distributionlist__project__slug=self.kwargs["prj"]
        )

    @extend_schema(
        responses={200: DistributionMemberSerializer(many=True)},
        description=_("List all members (assignments) of a specific distribution list."),
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
