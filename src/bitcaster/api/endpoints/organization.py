import logging

from rest_framework import serializers

from bitcaster.models import Organization

from .base import BaseModelViewSet

logger = logging.getLogger(__name__)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        read_only_fields = ('token', 'owner')
        write_only_fields = ('password',)
        fields = ['name', 'slug', 'id']


class OrganizationViewSet(BaseModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    # filter_backends = (IsOwnerFilter,)
