from typing import Any

from google.auth.transport._http_client import Response
from rest_framework import serializers
from django.http import HttpRequest
from rest_framework.reverse import reverse
from bitcaster.models import Address, Channel, Project, Application, Event
from rest_framework.decorators import action

from bitcaster.utils.http import absolute_reverse


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("name", "protocol")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("value", "type", "name")


class ProjectSerializer(serializers.ModelSerializer):
    applications = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("name", "slug", "applications")

    def get_applications(self, obj: Project):
        return absolute_reverse("api:project-applications-list", args=[obj.organization.slug, obj.slug])


class ApplicationSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ("name", "slug", "events")

    def get_events(self, obj: Application):
        return absolute_reverse(
            "api:project-applications-events", args=[obj.project.organization.slug, obj.project.slug, obj.slug]
        )


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
