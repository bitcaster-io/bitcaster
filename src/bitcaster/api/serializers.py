from rest_framework import serializers

from bitcaster.models import Channel


class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = ("name", "protocol")
