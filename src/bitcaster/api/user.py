from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import AddressSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import bitcaster
from bitcaster.models import Organization, User, UserRole


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(read_only=True)

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
        )

    def create(self, validated_data: dict[str, Any]) -> User:
        org: Organization = self.context["view"].organization
        email = validated_data.get("email")
        if not (user := User.objects.filter(email=email).first()):
            user = User.objects.create(username=email, email=email)

        UserRole.objects.get_or_create(user=user, organization=org, group=bitcaster.get_default_group())
        user.addresses.get_or_create(value=email)

        return user


class UserView(SecurityMixin, ViewSet, ListAPIView, CreateAPIView, RetrieveAPIView):
    serializer_class = UserSerializer
    required_grants = [Grant.USER_READ, Grant.USER_WRITE]

    @property
    def organization(self) -> "Organization":
        return Organization.objects.get(slug=self.kwargs["org"])

    def get_queryset(self) -> QuerySet[User]:
        return self.organization.users.all()

    def get_object(self) -> "User":
        return self.get_queryset().get(username=self.kwargs["username"])

    @extend_schema(description=_("List Organization's users"))
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(description=_("Creat an Organization's user"))
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)

    @extend_schema(
        request=UserSerializer,
        description=_("Update an Organization's user"),
    )
    @action(detail=True, methods=["PUT"])
    def update(self, request: HttpRequest, **kwargs: Any) -> Response:
        status_code = status.HTTP_200_OK
        user = self.get_object()
        ser = UserSerializer(instance=user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(ser.data, status=status_code)

    @extend_schema(request=AddressSerializer, responses=AddressSerializer, description=_("List User's addresses"))
    @action(detail=False, methods=["GET"], serializer_class=AddressSerializer)
    def list_address(self, request: HttpRequest, **kwargs: Any) -> Response:
        user = self.get_object()
        ser = AddressSerializer(many=True, instance=user.addresses.all())
        return Response(ser.data)

    @extend_schema(request=AddressSerializer, responses=AddressSerializer, description=_("Add an User's address"))
    @action(detail=True, methods=["POST"], serializer_class=AddressSerializer)
    def add_address(self, request: HttpRequest, **kwargs: Any) -> Response:
        user = self.get_object()
        status_code = status.HTTP_200_OK
        ser = AddressSerializer(data=request.POST)
        if ser.is_valid():
            ser.save(user=user)
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(ser.data, status=status_code)
