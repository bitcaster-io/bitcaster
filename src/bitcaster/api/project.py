from django.db.models import QuerySet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ProjectSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import Project


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
