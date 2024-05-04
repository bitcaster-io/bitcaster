from rest_framework import permissions, viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from ..models import Application, Channel, Event, Organization, Project, User
from .base import BaseModelViewSet, SecurityMixin
from .serializers import (
    ApplicationSerializer,
    ChannelSerializer,
    EventSerializer,
    OrganizationSerializer,
    ProjectSerializer,
    UserSerializer,
)


class SelectedOrganizationViewSet(SecurityMixin, viewsets.ReadOnlyModelViewSet):
    pass


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "slug"


class OrganizationViewSet(BaseModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = "slug"


class ProjectViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = Project.objects.all().order_by("-pk")
    serializer_class = ProjectSerializer
    lookup_field = "slug"
    # lookup_url_kwarg = "slug"


class ApplicationViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = Application.objects.all().order_by("-pk")
    serializer_class = ApplicationSerializer
    lookup_field = "slug"


class ChannelViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = Channel.objects.all().order_by("-pk")
    serializer_class = ChannelSerializer
    permission_classes = (permissions.DjangoObjectPermissions,)


class EventViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = Event.objects.all().order_by("-pk")
    serializer_class = EventSerializer
    permission_classes = (permissions.DjangoObjectPermissions,)
    lookup_field = "slug"

    # @action(
    #     detail=True,
    #     methods=[
    #         "GET",
    #     ],
    #     url_path=r"c",
    # )
    # def channels(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     return Response({})
    #
    # def trigger(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     obj = self.get_object()
    #     qs = obj.channels.all()
    #     serializer = ChannelSerializer(qs, many=True)
    #     return Response(serializer.data)
