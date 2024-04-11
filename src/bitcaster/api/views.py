from rest_framework import permissions, viewsets

from ..models import Organization
from .serializers import OrganizationSerializer


class SelectedOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    def selected_organization(self) -> Organization:
        return Organization.objects.get(id=self.kwargs["slug"])


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    lookup_field = "slug"

    # @action(detail=True)
    # def queries(self, **kwargs):
    #     return HttpResponseRedirect(reverse("api:queries-list", args=[kwargs["slug"]]))
