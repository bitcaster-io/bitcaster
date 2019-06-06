import logging

from crashlog.middleware import process_exception
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from bitcaster.api.filters import ApplicationFilterBackend
from bitcaster.models import Occurence
from bitcaster.tasks.event import trigger_event
from bitcaster.tsdb.api import log_error_event, log_new_occurence
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
            if not event.enabled:
                log_error_event(event, 'Event disabled')
                return Response({'error': 'Event disabled'}, status=400)
            occurence = Occurence.log(event=event)
            log_new_occurence(occurence)
            trigger_event.delay(occurence.pk,
                                request.data,
                                token=request.key.token,
                                origin=get_client_ip(request))
        except Exception as e:
            with atomic():
                process_exception(e)
            logger.exception(e)
            return Response({'message': str(e),
                             'timestamp': timezone.now()}, status=500)
        else:
            return Response({'message': 'Event triggered',
                             'id': occurence.pk,
                             'timestamp': timezone.now()}, status=201)
