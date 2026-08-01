from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .base import BaseView
from .permissions import ApiProjectPermission
from ..auth.constants import Grant
from ..models import Application, DistributionList, Project, User


class ApplicationUnregisterView(BaseView):
    required_grants = [Grant.MANAGE_APPLICATION_USERS]

    def post(self, request: Request, org: str, prj: str, app: str, username: str) -> Response:
        application = get_object_or_404(Application, slug=app, project__slug=prj, project__organization__slug=org)
        user = get_object_or_404(User, username=username, roles__organization=application.project.organization)

        through_model = DistributionList.recipients.through
        deleted, _ = through_model.objects.filter(
            distributionlist__application=application,
            assignment__address__user=user,
        ).delete()

        return Response({"deleted": deleted})


class ProjectUnregisterView(BaseView):
    permission_classes = (ApiProjectPermission,)
    required_grants = [Grant.MANAGE_PROJECT_USERS]

    def post(self, request: Request, org: str, prj: str, username: str) -> Response:
        project = get_object_or_404(Project, slug=prj, organization__slug=org)
        user = get_object_or_404(User, username=username, roles__organization=project.organization)

        through_model = DistributionList.recipients.through
        deleted, _ = through_model.objects.filter(
            distributionlist__project=project,
            assignment__address__user=user,
        ).delete()

        return Response({"deleted": deleted})
