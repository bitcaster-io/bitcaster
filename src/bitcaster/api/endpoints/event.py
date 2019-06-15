import logging

from crashlog.middleware import process_exception
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FileUploadParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from bitcaster.api.filters import ApplicationFilterBackend
from bitcaster.models import Occurence
from bitcaster.tasks.event import trigger_batch, trigger_event
from bitcaster.tsdb.api import log_error_event, log_new_occurence
from bitcaster.utils.http import flatten_query_dict
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
            authentication_classes=[],
            permission_classes=[],
            parser_classes=(JSONParser, FileUploadParser, MultiPartParser,),
            detail=True)
    def tr(self, request, organization__pk, application__pk, pk):
        key, pk = pk.split(':')
        app, key = TriggerKeyAuthentication().authenticate_credentials(request, key)
        perm = EventTriggerPermission()
        event = self.selected_application.events.get(pk=pk)
        if not perm.has_object_permission(request, self, event):
            raise PermissionDenied('Key not enabled for this event')
        return self.trigger(request, organization__pk, application__pk, pk)

    @action(methods=['get', 'post', 'options'],
            authentication_classes=[TriggerKeyAuthentication],
            permission_classes=[EventTriggerPermission],
            parser_classes=(JSONParser, FileUploadParser, MultiPartParser,),
            detail=True)
    def trigger(self, request, organization__pk, application__pk, pk):
        try:
            event = get_object_or_404(self.selected_application.events,
                                      pk=pk)
            if not event.enabled:
                log_error_event(event, 'Event disabled')
                return Response({'error': 'Event disabled'}, status=400)
            if request.method == 'GET':
                context = flatten_query_dict(request.query_params)
            else:
                context = flatten_query_dict(request.data)

            occurence = Occurence.log(event=event, context=context)
            log_new_occurence(occurence)
            trigger_event.delay(occurence.pk,
                                context,
                                token=request.key.token,
                                origin=get_client_ip(request))
        except Exception as e:
            logger.exception(e)
            with atomic():
                process_exception(e)
            return Response({'error': 500,
                             'message': str(e),
                             'timestamp': timezone.now()}, status=500)
        else:
            return Response({'message': 'Event triggered',
                             'event': event.pk,
                             'development': event.development_mode,
                             'id': occurence.pk,
                             'timestamp': timezone.now()}, status=201)

    @action(methods=['post', 'get', 'options'],
            authentication_classes=[TriggerKeyAuthentication],
            permission_classes=[EventTriggerPermission],
            parser_classes=(JSONParser, MultiPartParser,),
            detail=True)
    def batch(self, request, organization__pk, application__pk, pk):
        try:
            event = get_object_or_404(self.selected_application.events,
                                      pk=pk)
            if not event.enabled:
                log_error_event(event, 'Event disabled')
                return Response({'error': 'Event disabled'}, status=400)

            context = flatten_query_dict(request.data)
            if 'filter' not in context:
                raise ValidationError({'filter': 'Missing filter parameter'})
            if context['filter'] == 'address':
                context['filter'] = 'subscriber__addresses__address__in'
            elif context['filter'] == 'email':
                context['filter'] = 'subscriber__email__in'
            elif context['filter'].startswith('custom:'):
                __, field = context['filter'].split(':')
                context['filter'] = 'subscriber__extras__%s__in' % field
            else:
                raise ValidationError({'filter': 'Invalid filter parameter'})

            if 'targets' not in context:
                raise ValidationError({'targets': 'Missing targets parameter'})

            occurence = Occurence.log(event=event, context=context)
            log_new_occurence(occurence)

            trigger_batch.delay(occurence.pk,
                                context,
                                token=request.key.token,
                                origin=get_client_ip(request))

        except ValidationError as e:
            return Response({'error': 400,
                             'message': str(e),
                             'timestamp': timezone.now()}, status=400)
        except Exception as e:
            logger.exception(e)
            process_exception(e)
            return Response({'error': 500,
                             'message': str(e),
                             'timestamp': timezone.now()}, status=500)
        else:
            return Response({'message': 'Event triggered',
                             'event': event.pk,
                             'development': event.development_mode,
                             'id': occurence.pk,
                             'timestamp': timezone.now()}, status=201)
