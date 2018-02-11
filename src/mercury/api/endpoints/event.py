# -*- coding: utf-8 -*-
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from mercury import logging
from mercury.api.endpoints.application import token_required
from mercury.api.endpoints.base import BaseModelViewSet
from mercury.api.filters import ApplicationFilterBackend
from mercury.api.serializers import EventSerializer
from mercury.models import Event
from mercury.permissions import IsApplicationRelated
from mercury.tasks import trigger_event

logger = logging.getLogger(__name__)


class EventViewSet(BaseModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsApplicationRelated.create('application')]
    filter_backends = [ApplicationFilterBackend.create('application',
                                                       'application__pk')]

    def get_serializer(self, *args, **kwargs):
        ret = super().get_serializer(*args, **kwargs)
        ret.application = self.get_selected_application()
        return ret

    @token_required
    @detail_route(methods=['get', 'post'])
    def trigger(self, request, application__pk, pk):
        event = self.get_object()
        if not event.enabled:
            return Response({"error": "Event disabled"}, status=400)
        trigger_event.delay(event.id, request.data)
        return Response(status=201)
