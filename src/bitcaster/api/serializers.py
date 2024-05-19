from rest_framework import serializers

from bitcaster.models import Address, Channel


class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = ("name", "protocol")


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ("value", "type", "name")
