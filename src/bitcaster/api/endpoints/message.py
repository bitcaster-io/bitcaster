# -*- coding: utf-8 -*-
from bitcaster import logging
from bitcaster.models.message import Message

from ..filters import ApplicationFilterBackend, ApplicationOwnedFilter
from ..permissions import IsApplicationRelated
from ..serializers import MessageSerializer
from .base import BaseModelViewSet

logger = logging.getLogger(__name__)


class MessageViewSet(BaseModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsApplicationRelated.create('application')]
    filter_backends = [ApplicationOwnedFilter,
                       ApplicationFilterBackend.create('application__pk',
                                                       'event__application')
                       ]

    # def get_serializer(self, *args, **kwargs):
    #     return super().get_serializer(*args, **kwargs)

    #
    # def create(self, request, application__pk=None, *args, **kwargs):
    #     d = request.data
    #     app = self.get_selected_application()
    #     serializer = self.get_serializer(data=d, application=app)
    #     serializer.is_valid(raise_exception=True)
    #     # app = Application.objects.get(pk=application__pk)
    #     # self.check_object_permissions(request, app)
    #     #
    #     # event = app.events.get(pk=d['event'])
    #     #
    #     # d['producer'] = app.pk
    #     # d['application'] = app.pk
    #     #
    #     # self.perform_create(serializer)
    #     # headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
