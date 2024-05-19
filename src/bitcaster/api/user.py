from django.db.models import QuerySet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from bitcaster.api.base import SecurityMixin
from bitcaster.api.serializers import AddressSerializer
from bitcaster.auth.constants import Grant
from bitcaster.constants import Bitcaster
from bitcaster.models import DistributionList, Organization, User, UserRole


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

    def create(self, validated_data):
        org: Organization = self.context["view"].organization
        email = validated_data.get("email")
        if not (user := User.objects.filter(email=email).first()):
            user = User.objects.create(username=email, email=email)

        UserRole.objects.get_or_create(user=user, organization=org, group=Bitcaster.get_default_group())
        user.addresses.get_or_create(value=email)

        return user


class UserView(SecurityMixin, ViewSet, ListAPIView, CreateAPIView, RetrieveAPIView):
    serializer_class = UserSerializer
    required_grants = [Grant.USER_READ, Grant.USER_WRITE]

    @property
    def organization(self) -> "Organization":
        return Organization.objects.get(slug=self.kwargs["org"])

    def get_queryset(self) -> QuerySet[DistributionList]:
        return self.organization.users.all()

    def get_object(self) -> "User":
        return self.get_queryset().get(username=self.kwargs["username"])

    @action(detail=True, methods=["PUT"])
    def update(self, request, pk=None, **kwargs):
        status_code = status.HTTP_200_OK
        user = self.get_object()
        ser = UserSerializer(instance=user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(ser.data, status=status_code)

    @action(detail=True, methods=["GET", "POST"], serializer_class=AddressSerializer)
    def address(self, request, org, username, **kwargs):
        user = self.get_object()
        status_code = status.HTTP_200_OK
        if request.method == "GET":
            ser = AddressSerializer(many=True, instance=user.addresses.all())
            return Response(ser.data)
        else:  # request.method == "POST":
            ser = AddressSerializer(data=request.POST)
            if ser.is_valid():
                ser.save(user=user)
            else:
                status_code = status.HTTP_400_BAD_REQUEST
            return Response(ser.data, status=status_code)
