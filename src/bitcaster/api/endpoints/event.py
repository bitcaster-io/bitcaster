import logging

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from sentry_sdk import capture_event

from bitcaster.api.filters import ApplicationFilterBackend
from bitcaster.logging import log_occurence
from bitcaster.tasks import trigger_event
from bitcaster.tsdb.logging import broker
from bitcaster.utils.wsgi import get_client_ip

from ...models.event import Event
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
    parser_classes = (FileUploadParser, JSONParser, MultiPartParser,)

    # def get_serializer(self, *args, **kwargs):
    #     ret = super().get_serializer(*args, **kwargs)
    #     ret.application = self.get_selected_application()
    #     return ret

    @action(methods=['get', 'post', 'options'],
            authentication_classes=[TriggerKeyAuthentication],
            permission_classes=[EventTriggerPermission],
            parser_classes=(JSONParser, FileUploadParser, MultiPartParser,),
            detail=True)
    def trigger(self, request, organization__pk, application__pk, pk):
        try:
            event = self.get_object()
            # Counter.objects.initialize(event)
            broker.get_ts(organization__pk)
            log_occurence(event)
            if not event.enabled:
                return Response({'error': 'Event disabled'}, status=400)

            trigger_event.delay(event.id, request.data,
                            token=request.key.token,
                            origin=get_client_ip(request))
        except Exception as e:
            capture_event()
            logger.exception(e)
            return Response({'message': str(e),
                             'timestamp': timezone.now()}, status=500)

        return Response({'message': 'Event triggered',
                         'subscriptions': event.subscriptions.count(),
                         'timestamp': timezone.now()}, status=201)
