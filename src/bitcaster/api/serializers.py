from rest_framework import serializers
from strategy_field.utils import fqn

from bitcaster.models import Address, Application, Channel, Event, Project
from bitcaster.utils.http import absolute_reverse


class ChannelSerializer(serializers.ModelSerializer):
    dispatcher = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ("name", "protocol", "dispatcher", "locked")

    def get_dispatcher(self, obj: Channel) -> str:
        return fqn(obj.dispatcher)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("value", "type", "name")


class ProjectSerializer(serializers.ModelSerializer):
    applications = serializers.SerializerMethodField()
    lists = serializers.SerializerMethodField()
    channels = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("name", "slug", "applications", "lists", "channels")

    def get_applications(self, obj: Project) -> str:
        return absolute_reverse("api:project-application-list", args=[obj.organization.slug, obj.slug])

    def get_lists(self, obj: Project) -> str:
        return absolute_reverse("api:distribution-list", args=[obj.organization.slug, obj.slug])

    def get_channels(self, obj: Project) -> str:
        return absolute_reverse("api:project-channel-list", args=[obj.organization.slug, obj.slug])


class ApplicationSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ("name", "slug", "events")

    def get_events(self, obj: Application) -> str:
        return absolute_reverse("api:events-list", args=[obj.project.organization.slug, obj.project.slug, obj.slug])


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
