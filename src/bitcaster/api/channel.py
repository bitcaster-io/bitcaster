from django.db.models import QuerySet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ViewSet

from ..auth.constants import Grant
from ..models import Channel
from .base import SecurityMixin
from .serializers import ChannelSerializer

app_name = "api"


class ChannelView(SecurityMixin, ViewSet, ListAPIView, RetrieveAPIView):
    """
    List application events
    """

    serializer_class = ChannelSerializer
    required_grants = [Grant.ORGANIZATION_READ]

    def get_queryset(self) -> QuerySet[Channel]:
        if "prj" in self.kwargs:
            return Channel.objects.filter(
                organization__slug=self.kwargs["org"],
                project__slug=self.kwargs["prj"],
            )
        elif "org" in self.kwargs:
            return Channel.objects.filter(
                organization__slug=self.kwargs["org"],
            )
