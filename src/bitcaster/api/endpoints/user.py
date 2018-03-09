# -*- coding: utf-8 -*-
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from bitcaster import logging
from bitcaster.models import User

from ..filters import IsAdministratorOrSameUser
from ..permissions import DjangoModelPermissions, SameUser
from ..serializers import (CreateUserSerializer,
                           PasswordSerializer, UserSerializer,)
from .base import BaseModelViewSet

logger = logging.getLogger(__name__)


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (DjangoModelPermissions, SameUser)
    filter_backends = (IsAdministratorOrSameUser,)

    def get_queryset(self):
        return super().get_queryset()

    def check_permissions(self, request):
        return True

    def check_object_permissions(self, request, obj):
        if request.user.is_anonymous:
            self.permission_denied(request)

        if request.user == obj:
            return True
        super().check_permissions(request)

    def get_serializer_class(self):
        if self.action == 'create' and self.request.method == 'POST':
            return CreateUserSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        super().perform_create(serializer)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @detail_route(methods=['post'], permission_classes=[SameUser])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.password = serializer.data['password1']
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

            # @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
            # def subscription(self, request, pk=None, channel=None):
            #     manager = ChildManager(self, SubscriptionSerializer, 'subscriber', 'subscriptions')
            #     manager.check_owner(request, self.get_object())
            # return manager.process(request)

            # @list_route(methods=['get'], permission_classes=[IsAuthenticated])
            # def applications(self, request):
            #     ser = ApplicationSerializer(request.user.applications.all(), many=True)
            #     return Response(ser.data)
