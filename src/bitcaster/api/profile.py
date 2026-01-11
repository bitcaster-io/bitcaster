from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import AddressSerializer, UserMessageSerializer
from bitcaster.auth.constants import Grant
from bitcaster.console.utils import get_unseen_message_for_user
from bitcaster.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "locked")


class UserProfileView(SecurityMixin, ViewSet, RetrieveAPIView):
    serializer_class = UserProfileSerializer
    required_grants = [Grant.USER_PROFILE]

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.all()

    def get_object(self) -> "User":
        return self.request.user

    @extend_schema(request=AddressSerializer, responses=AddressSerializer, description=_("List User's addresses"))
    def addresses(self, request: HttpRequest, **kwargs: Any) -> Response:
        user = self.get_object()
        ser = AddressSerializer(many=True, instance=user.addresses.all())
        return Response(ser.data)

    @extend_schema(
        request=UserMessageSerializer, responses=UserMessageSerializer, description=_("List User's messages")
    )
    def messages(self, request: HttpRequest) -> Response:
        ser = UserMessageSerializer(many=True, instance=request.user.bitcaster_messages.all())
        return Response(ser.data)

    @extend_schema(
        request=UserMessageSerializer, responses=UserMessageSerializer, description=_("Retrieve unseen user messages")
    )
    def unseen(self, request: HttpRequest, **kwargs: Any) -> Response:
        user: User = self.get_object()
        ser = UserMessageSerializer(many=True, instance=get_unseen_message_for_user(user.pk))
        return Response(ser.data)
