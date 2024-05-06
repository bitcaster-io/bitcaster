from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from bitcaster.models import Application, Channel, Event, Organization, Project, User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")


class SelecteOrganizationSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()


class OrganizationSerializer(serializers.ModelSerializer):

    # hyperlinks
    links = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("id", "slug", "name")


class ProjectSerializer(SelecteOrganizationSerializer):

    class Meta:
        model = Project
        fields = ("name", "slug", "organization")


class ApplicationSerializer(SelecteOrganizationSerializer):

    class Meta:
        model = Application
        fields = ("name",)


class ChannelSerializer(ModelSerializer):

    class Meta:
        model = Channel
        exclude = ()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
