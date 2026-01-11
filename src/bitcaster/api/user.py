from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import AddressSerializer, UserMessageSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import bitcaster
from bitcaster.models import Organization, User, UserRole
from bitcaster.utils.http import absolute_reverse
from bitcaster.utils.json import JsonUpdateMode, process_dict


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "custom_fields")

    def create(self, validated_data: dict[str, Any]) -> User:
        org: Organization = self.context["view"].organization
        email = validated_data.get("email")

        if not (user := User.objects.filter(email=email).first()):
            user = User.objects.create(username=email, **validated_data)

        UserRole.objects.get_or_create(user=user, organization=org, group=bitcaster.get_default_group())
        user.addresses.get_or_create(name="email", value=email)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    _mode = serializers.ChoiceField(choices=JsonUpdateMode.choices, default=JsonUpdateMode.IGNORE)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "locked", "custom_fields", "_mode")

    def validate(self, attrs):
        ret = super().validate(attrs)
        if "custom_fields" in ret:
            if attrs["_mode"] == JsonUpdateMode.IGNORE:
                del ret["custom_fields"]
            else:
                custom_fields = process_dict(self.instance.custom_fields, attrs["custom_fields"], attrs["_mode"])
                ret["custom_fields"] = custom_fields
        return ret


class UserSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "url", "email", "username", "first_name", "last_name", "locked")

    def get_url(self, obj: User) -> str:
        return absolute_reverse("api:user-update", args=[self.context["view"].kwargs["org"], obj.username])


class UserDetailSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "locked", "messages", "addresses")

    def get_messages(self, obj: User) -> str:
        return absolute_reverse("api:user-messages", args=[self.context["view"].kwargs["org"], obj.username])

    def get_addresses(self, obj: User) -> str:
        return absolute_reverse("api:user-addresses", args=[self.context["view"].kwargs["org"], obj.username])


class UserView(SecurityMixin, ViewSet, ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView):
    serializer_class = UserSerializer
    required_grants = [Grant.USER_READ, Grant.USER_WRITE]
    action_serializers = {
        "create": UserCreateSerializer,
        "list": UserSerializer,
        "retrieve": UserDetailSerializer,
        "update": UserUpdateSerializer,
        "patch": UserUpdateSerializer,
    }

    @property
    def organization(self) -> "Organization":
        return Organization.objects.get(slug=self.kwargs["org"])

    def get_queryset(self) -> QuerySet[User]:
        return self.organization.users.all()

    def get_object(self) -> "User":
        return self.get_queryset().get(username=self.kwargs["username"])

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

    @extend_schema(
        request=UserMessageSerializer, responses=UserMessageSerializer, description=_("Retrieve user messages")
    )
    @action(detail=True, methods=["GET"], serializer_class=UserMessageSerializer)
    def list_messages(self, request: HttpRequest, **kwargs: Any) -> Response:
        user: User = self.get_object()
        ser = UserMessageSerializer(many=True, instance=user.bitcaster_messages.all())
        return Response(ser.data)
