# -*- coding: utf-8 -*-
import logging

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from bitcaster.api.filters import ApplicationFilterBackend
from bitcaster.models import Event
from bitcaster.tasks import trigger_event
from bitcaster.utils.wsgi import get_client_ip

from ..permissions import (EventTriggerPermission, IsApplicationRelated,
                           TriggerKeyAuthentication,)
from ..serializers import EventSerializer
from .base import BaseModelViewSet

logger = logging.getLogger(__name__)


class EventViewSet(BaseModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsApplicationRelated.create('application')]
    filter_backends = [ApplicationFilterBackend]
    parser_classes = (FileUploadParser,)

    # def get_serializer(self, *args, **kwargs):
    #     ret = super().get_serializer(*args, **kwargs)
    #     ret.application = self.get_selected_application()
    #     return ret

    @action(methods=['get', 'post'],
            authentication_classes=[TriggerKeyAuthentication],
            permission_classes=[EventTriggerPermission],
            detail=True)
    def trigger(self, request, application__pk, pk):
        event = self.get_object()
        if not event.enabled:
            return Response({'error': 'Event disabled'}, status=400)
        trigger_event.delay(event.id, request.data,
                            token=request.key.token,
                            origin=get_client_ip(request))
        return Response({'message': 'Event triggered',
                         'subscriptions': event.subscriptions.count(),
                         'timestamp': timezone.now()}, status=201)
