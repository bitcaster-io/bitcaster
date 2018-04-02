from bitcaster import logging
from bitcaster.models import Application

from ..filters import IsOwnerFilter
from ..permissions import IsOwnerOrMaintainter
from ..serializers import ApplicationSerializer
from .base import BaseModelViewSet

logger = logging.getLogger(__name__)


# def token_required(func):
#     @wraps(func)
#     def _wrapped_view(_, request, *args, **kwargs):
#         if not getattr(request, 'token', False):
#             return Response(status=403)
#         return func(_, request, *args, **kwargs)
#
#     return _wrapped_view


class ApplicationViewSet(BaseModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    search_fields = ('name',)
    permission_classes = (IsOwnerOrMaintainter,)
    filter_backends = (IsOwnerFilter,)

    # lookup_url_kwarg = 'application__pk'
    # def get_serializer(self, *args, **kwargs):
    #     kwargs['owner'] = self.request.user
    #     return super().get_serializer(*args, **kwargs)

    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    # def check_permissions(self, request):
    #     super().check_permissions(request)

    # def get_object(self):
    #     return super().get_object()

    # def perform_update(self, serializer):
    #     # serializer.validated_data['owner'] = self.request.user
    #     super().perform_update(serializer)

    # def perform_create(self, serializer):
    #     serializer.save()
    #     ApiAuthToken.objects.create(application=serializer.instance,
    #                                 token=ApiAuthToken.generate_token(),
    #                                 user=serializer.instance.owner)
    #
    # # @detail_route(methods=['post'], permission_classes=[IsOwner],
    #               url_name='generate-token')
    # def generate_token(self, request, pk):
    #     app = self.get_object()
    #     token = ApiAuthToken.objects.create(application=app,
    #                                         user=request.user)
    #     return Response({'token': token.token},
    #                     status=201)
