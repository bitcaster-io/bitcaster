# -*- coding: utf-8 -*-
from bitcaster import logging
from bitcaster.models import Channel

from ..filters import ApplicationOwnedFilter
from ..permissions import IsApplicationRelated
from ..serializers import ChannelSerializer
from .base import BaseModelViewSet

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
