# -*- coding: utf-8 -*-
from functools import wraps

from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from mercury import logging
from mercury.api.endpoints.base import BaseModelViewSet
from mercury.api.filters import IsOwnerFilter
from mercury.api.serializers import ApplicationSerializer, MaintainerSerializer
from mercury.models import ApiAuthToken, Application, User
from mercury.permissions import IsOwner, IsOwnerOrMaintainter

logger = logging.getLogger(__name__)


def token_required(func):
    @wraps(func)
    def _wrapped_view(_, request, *args, **kwargs):
        if not getattr(request, 'token', False):
            return Response(status=403)
        return func(_, request, *args, **kwargs)

    return _wrapped_view


class ApplicationViewSet(BaseModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = (IsOwnerOrMaintainter,)
    search_fields = ('name',)
    filter_backends = (IsOwnerFilter,)
    # lookup_url_kwarg = 'application__pk'
    # def get_serializer(self, *args, **kwargs):
    #     kwargs['owner'] = self.request.user
    #     return super().get_serializer(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def check_permissions(self, request):
        super().check_permissions(request)

    def get_object(self):
        return super().get_object()

    # def perform_update(self, serializer):
    #     # serializer.validated_data['owner'] = self.request.user
    #     super().perform_update(serializer)

    def perform_create(self, serializer):
        serializer.save()
        ApiAuthToken.objects.create(application=serializer.instance,
                                    token=ApiAuthToken.generate_token(),
                                    user=serializer.instance.owner)

    @detail_route(methods=['post'], permission_classes=[IsOwner])
    def add_maintainer(self, request, pk=None):
        app = self.get_object()
        self.check_object_permissions(request, app)
        serializer = MaintainerSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            try:
                app.maintainers.add(User.objects.get(email=email))
            except User.DoesNotExist:  # pragma: no cover
                # could be deleted during transaction
                raise Exception('User not found')
            return Response({'status': 'user {} has been added as maintainer'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsOwner],
                  url_name='generate-token')
    def generate_token(self, request, pk):
        app = self.get_object()
        token = ApiAuthToken.objects.create(application=app,
                                    user=request.user)
        return Response({'token': token.token},
                        status=201)
