from django.db.models import QuerySet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import DistributionList, Organization, Project, User, UserRole


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        exclude = (
            "password",
            "last_login",
            "is_superuser",
            "is_staff",
            "date_joined",
            "groups",
            "user_permissions",
            "username",
        )

    def create(self, validated_data):
        org: Organization = self.context["view"].organization

        if user := User.objects.filter(email=validated_data["email"]).first():
            UserRole.objects.get_or_create(user=user, organization=org, group=Bitcaster.get_default_group())
        else:
            validated_data["username"] = validated_data["email"]
            user = super().create(validated_data)

        return user


class UserView(SecurityMixin, ViewSet, ListAPIView, CreateAPIView, RetrieveAPIView):
    serializer_class = UserSerializer
    required_grants = [Grant.USER_READ, Grant.USER_WRITE]

    @property
    def organization(self) -> "Project":
        return Organization.objects.get(slug=self.kwargs["org"])

    def get_queryset(self) -> QuerySet[DistributionList]:
        return User.objects.filter(roles__organization=self.organization)

    # @action(detail=True, methods=["GET"])
    # def roles(self, request, pk=None, **kwargs):
    #     dl: DistributionList = self.get_object()
    #     try:
    #         data = json.loads(request.body)
    #         for entry in data:
    #             Address.objects.filter()
    #         return Response({"message": data, "dl": dl.pk})
    #     except Exception as e:
    #         return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PUT"])
    def update(self, request, pk=None, **kwargs):
        return Response({"error": "---"}, status=status.HTTP_400_BAD_REQUEST)

    #
    #
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    # #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
