from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .base import SecurityMixin
from .serializers import AddressSerializer, UserMessageSerializer
from ..auth.constants import Grant
from ..constants import bitcaster
from ..models import Organization, User, UserRole
from ..utils.http import absolute_reverse
from ..utils.json import JsonUpdateMode, process_dict


class UserCreateSerializer(serializers.ModelSerializer[User]):
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


class UserUpdateSerializer(serializers.ModelSerializer[User]):
    _mode = serializers.ChoiceField(choices=JsonUpdateMode.choices, default=JsonUpdateMode.IGNORE)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "locked", "custom_fields", "_mode")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        ret = super().validate(attrs)
        if "custom_fields" in ret:
            if attrs["_mode"] == JsonUpdateMode.IGNORE:
                del ret["custom_fields"]
            else:
                custom_fields = process_dict(self.instance.custom_fields, attrs["custom_fields"], attrs["_mode"])
                ret["custom_fields"] = custom_fields
        return ret


class UserSerializer(serializers.ModelSerializer[User]):
    url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "url", "email", "username", "first_name", "last_name", "locked")

    def get_url(self, obj: User) -> str:
        return absolute_reverse("api:user-update", args=[self.context["view"].kwargs["org"], obj.username])


class UserDetailSerializer(serializers.ModelSerializer[User]):
    messages = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "locked", "messages", "addresses")

    def get_messages(self, obj: User) -> str:
        return absolute_reverse("api:user-messages", args=[self.context["view"].kwargs["org"], obj.username])

    def get_addresses(self, obj: User) -> str:
        return absolute_reverse("api:user-addresses", args=[self.context["view"].kwargs["org"], obj.username])


class UserView(
    SecurityMixin, ViewSet, ListAPIView[User], CreateAPIView[User], UpdateAPIView[User], RetrieveAPIView[User]
):
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

    @extend_schema(
        responses={200: UserSerializer(many=True)}, description=_("List all users belonging to the organization.")
    )
    def list(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=UserCreateSerializer,
        responses={201: UserSerializer},
        description=_(
            "Register a new user in the organization. "
            "If the user already exists in the system, they will be linked to this organization."
        ),
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().create(request, *args, **kwargs)

    @extend_schema(
        responses={200: UserDetailSerializer},
        description=_(
            "Retrieve comprehensive details of a specific user, including their messaging and address endpoints."
        ),
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        description=_(
            "Update user details. Supports a specialized '_mode' for handling updates to custom_fields (JSON)."
        ),
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=AddressSerializer,
        responses={200: AddressSerializer(many=True)},
        description=_("Retrieve all communication addresses (email, phone, etc.) configured for a specific user."),
    )
    @action(detail=False, methods=["GET"], serializer_class=AddressSerializer)
    def list_address(self, request: Request, **kwargs: Any) -> Response:
        user = self.get_object()
        ser = AddressSerializer(many=True, instance=user.addresses.all())
        return Response(ser.data)

    @extend_schema(
        request=AddressSerializer,
        responses={201: AddressSerializer},
        description=_("Add a new communication address to a user's profile."),
    )
    @action(detail=True, methods=["POST"], serializer_class=AddressSerializer)
    def add_address(self, request: HttpRequest, **kwargs: Any) -> Response:
        user = self.get_object()
        status_code: int = status.HTTP_201_CREATED
        ser = AddressSerializer(data=request.POST)
        if ser.is_valid():
            ser.save(user=user)
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(ser.data, status=status_code)

    @extend_schema(
        responses={200: UserMessageSerializer(many=True)},
        description=_("Retrieve the complete notification history for a specific user within the organization."),
    )
    @action(detail=True, methods=["GET"], serializer_class=UserMessageSerializer)
    def list_messages(self, request: Request, **kwargs: Any) -> Response:
        user: User = self.get_object()
        ser = UserMessageSerializer(many=True, instance=user.bitcaster_messages.all())
        return Response(ser.data)
