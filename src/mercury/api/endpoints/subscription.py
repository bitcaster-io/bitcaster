# -*- coding: utf-8 -*-
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from mercury import logging
from mercury.api.endpoints.base import BaseModelViewSet
from mercury.api.filters import UserFilterBackend
from mercury.api.serializers import SubscriptionSerializer
from mercury.models.subscription import Subscription

logger = logging.getLogger(__name__)


class SubscriptionViewSet(BaseModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = [UserFilterBackend.create('subscriber',
                                                'user__pk')]

    @detail_route(methods=['get'])
    def deactivate(self, request, user__pk, pk):
        subscription = self.get_object()
        token = self.request.GET.get('token', '')
        if subscription.deactivation_token == token:
            subscription.active = False
            subscription.save()
            return Response(status=200)
        else:
            return Response({"error": "Invalid token"}, status=400)
