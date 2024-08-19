from django.db.models import QuerySet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import ApplicationSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import Application, Organization


class ApplicationView(SecurityMixin, ViewSet, RetrieveAPIView, ListAPIView):
    """
    Application details
    """

    serializer_class = ApplicationSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "app"
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Organization]:
        return Application.objects.exclude(project__organization_id=Bitcaster.app.organization.pk).filter(
            project__organization__slug=self.kwargs["org"],
            project__slug=self.kwargs["prj"],
        )

    # @action(detail=True, methods=["GET"], description="Events list", __doc__="aaaaaaa")
    # def events(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     app: Application = self.get_object()
    #     ser = EventSerializer(many=True, instance=app.events.all())
    #     return Response(ser.data)

    # @action(detail=True, methods=["GET"], description="Channel list")
    # def projects(self, request: HttpRequest, **kwargs: Any) -> Response:
    #     org: Organization = self.get_object()
    #     ser = ProjectSerializer(many=True, instance=org.projects.filter())
    #     return Response(ser.data)
