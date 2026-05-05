from typing import Any, cast

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from .base import SecurityMixin
from .serializers import AddressSerializer, UserMessageSerializer
from ..auth.constants import Grant
from ..console.utils import get_unseen_message_for_user
from ..models import User


class UserProfileSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "locked")


class UserProfileView(SecurityMixin, ViewSet, RetrieveAPIView[User]):
    serializer_class = UserProfileSerializer
    required_grants = [Grant.USER_PROFILE]

    def get_queryset(self) -> QuerySet[User]:
        raise NotImplementedError

    def get_object(self) -> "User":
        return cast("User", self.request.user)

    @extend_schema(
        responses={200: UserProfileSerializer},
        description=_("Retrieve basic profile information for the currently authenticated user (Self)."),
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        responses={200: AddressSerializer(many=True)},
        description=_(
            "List all communication addresses (email, phone, push tokens, etc.) configured for the authenticated user."
        ),
    )
    def addresses(self, request: Request, **kwargs: Any) -> Response:
        user = self.get_object()
        ser = AddressSerializer(many=True, instance=user.addresses.all())
        return Response(ser.data)

    @extend_schema(
        responses={200: UserMessageSerializer(many=True)},
        description=_("Retrieve the full history of notifications sent to the authenticated user."),
    )
    def messages(self, request: Request) -> Response:
        ser = UserMessageSerializer(many=True, instance=request.user.bitcaster_messages.all())
        return Response(ser.data)

    @extend_schema(
        responses={200: UserMessageSerializer(many=True)},
        description=_(
            "Retrieve a list of notifications that have been sent but not yet marked as seen by the authenticated user."
        ),
    )
    def unseen(self, request: Request, **kwargs: Any) -> Response:
        user: User = self.get_object()
        ser = UserMessageSerializer(many=True, instance=get_unseen_message_for_user(user.pk))
        return Response(ser.data)
