from typing import Any

from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.auth.constants import Grant
from bitcaster.constants import bitcaster
from bitcaster.models import Organization
from bitcaster.utils.http import absolute_uri


class OrgSerializer(serializers.ModelSerializer[Organization]):
    users = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    channels = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("name", "slug", "users", "projects", "channels")

    def get_users(self, obj: Organization) -> str:
        return absolute_uri(reverse("api:user-list", kwargs={"org": obj.slug}))

    def get_projects(self, obj: Organization) -> str:
        return absolute_uri(reverse("api:project-list", kwargs={"org": obj.slug}))

    def get_channels(self, obj: Organization) -> str:
        return absolute_uri(reverse("api:org-channel-list", kwargs={"org": obj.slug}))


class OrgView(SecurityMixin, ViewSet, RetrieveAPIView[Organization]):
    """Organization details."""

    serializer_class = OrgSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "org"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Organization]:
        return Organization.objects.exclude(id=bitcaster.app.organization.pk)

    @extend_schema(
        responses={200: OrgSerializer},
        description=_(
            "Retrieve details of a specific organization, including links to its users, projects, and channels."
        ),
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)
