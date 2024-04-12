from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from strategy_field.utils import fqn

from bitcaster.models import Application, Channel, Event, Organization, Project, User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")


class OrganizationSerializer(HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:organization-detail", lookup_field="slug", read_only=True)

    projects = serializers.HyperlinkedIdentityField(
        view_name="api:organization:project-list", lookup_field="projects", read_only=True
    )

    class Meta:
        model = Organization
        exclude = ("owner",)


class ProjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Project
        exclude = ("owner",)


class ApplicationSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Application
        exclude = ()


class ChannelSerializer(HyperlinkedModelSerializer):
    dispatcher = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        exclude = ()

    def get_dispatcher(self, obj: Channel) -> str:
        return fqn(obj.dispatcher)


class EventSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Event
        exclude = ()
