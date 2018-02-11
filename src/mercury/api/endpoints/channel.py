# -*- coding: utf-8 -*-
from mercury import logging
from mercury.api.endpoints.base import BaseModelViewSet
from mercury.api.filters import ApplicationOwnedFilter
from mercury.api.serializers import ChannelSerializer
from mercury.models import Channel
from mercury.permissions import IsApplicationRelated

logger = logging.getLogger(__name__)


class ChannelViewSet(BaseModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsApplicationRelated.create('application')]
    filter_backends = [ApplicationOwnedFilter,
                       # ApplicationFilterBackend.create('application', 'application_pk')
                       ]

    def get_serializer(self, *args, **kwargs):
        ret = super().get_serializer(*args, **kwargs)
        ret.application = self.get_selected_application()
        return ret
