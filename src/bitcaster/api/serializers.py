from rest_framework import serializers

from bitcaster.models import Event, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = ()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("__all__",)
