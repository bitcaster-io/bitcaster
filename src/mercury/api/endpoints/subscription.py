# -*- coding: utf-8 -*-
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

    # def perform_create(self, serializer):
    #     serializer.save(subscriber=self.request.user)
    #
    # def perform_update(self, serializer):
    #     serializer.save(subscriber=self.request.user)
