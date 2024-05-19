import json

from django.db.models import QuerySet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.auth.constants import Grant
from bitcaster.models import Assignment, DistributionList, Organization, Project


class DistributionAddSerializer(serializers.Serializer):
    address = serializers.CharField()


class DistributionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DistributionList
        fields = ("name", "id")

    def validate_name(self, value):
        view: DistributionView = self.context["view"]
        if DistributionList.objects.filter(name__exact=value, project=view.project).exists():
            raise serializers.ValidationError("Name already exists!")
        return value

    def create(self, validated_data):
        validated_data["project"] = self.context["view"].project
        return super().create(validated_data)


class DistributionView(SecurityMixin, ViewSet, ListAPIView, CreateAPIView, RetrieveAPIView):
    """
    Distribution list
    """

    serializer_class = DistributionListSerializer
    required_grants = [Grant.DISTRIBUTION_LIST]

    @property
    def project(self) -> "Project":
        return Project.objects.select_related("organization").get(
            organization__slug=self.kwargs["org"], slug=self.kwargs["prj"]
        )

    @property
    def organization(self) -> "Organization":
        return self.project.organization

    def get_queryset(self) -> QuerySet[DistributionList]:
        return DistributionList.objects.filter(
            project__organization__slug=self.kwargs["org"], project__slug=self.kwargs["prj"]
        )

    @action(detail=True, methods=["POST"], description="aaaaa")
    def add(self, request, pk=None, **kwargs):
        dl: DistributionList = self.get_object()
        try:
            data = json.loads(request.body)
            asms = Assignment.objects.filter(address__value__in=data)
            dl.recipients.add(*asms)
            return Response({"message": data, "added": asms.values_list("address__value", flat=True)})
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
