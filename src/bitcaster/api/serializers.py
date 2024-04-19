from django.db.models import Model
from django.utils.functional import cached_property
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from strategy_field.utils import fqn

from bitcaster.models import Application, Channel, Event, Organization, Project, User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")


class SelecteOrganizationSerializer(serializers.ModelSerializer):
    co_key = "parent_lookup_organization__slug"
    organization = serializers.SerializerMethodField()

    @cached_property
    def selected_organization(self) -> Organization:
        kwargs = self.context["view"].kwargs
        co_slug: str = kwargs[self.co_key]
        return Organization.objects.get(slug=co_slug)

    def get_organization(self, obj: Model) -> str:
        return self.context["request"].build_absolute_uri(
            reverse("api:organization-detail", args=[self.selected_organization.slug])
        )


class OrganizationSerializer(HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:organization-detail", lookup_field="slug", read_only=True)
    projects = serializers.HyperlinkedIdentityField(
        view_name="api:project-list", lookup_field="slug", lookup_url_kwarg="parent_lookup_organization__slug"
    )
    channels = serializers.HyperlinkedIdentityField(
        view_name="api:org-channel-list", lookup_field="slug", lookup_url_kwarg="parent_lookup_organization__slug"
    )

    class Meta:
        model = Organization
        exclude = ("owner",)


class ProjectSerializer(SelecteOrganizationSerializer):
    co_key = "parent_lookup_organization__slug"
    url = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    channels = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("url", "name", "slug", "organization", "applications", "channels")

    def get_url(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:project-detail",
                args=[kwargs["parent_lookup_organization__slug"], obj.slug],
            )
        )

    def get_applications(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:application-list",
                args=[kwargs["parent_lookup_organization__slug"], obj.slug],
            )
        )

    def get_channels(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:prj-channel-list",
                args=[
                    kwargs["parent_lookup_organization__slug"],
                    obj.slug,
                ],
            )
        )


class ApplicationSerializer(SelecteOrganizationSerializer):
    co_key = "parent_lookup_project__organization__slug"
    url = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ("name", "organization", "url", "events")

    def get_url(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:application-detail",
                args=[
                    kwargs["parent_lookup_project__organization__slug"],
                    kwargs["parent_lookup_project__slug"],
                    obj.slug,
                ],
            )
        )

    def get_events(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:event-list",
                args=[
                    kwargs["parent_lookup_project__organization__slug"],
                    kwargs["parent_lookup_project__slug"],
                    obj.slug,
                ],
            )
        )


class ChannelSerializer(ModelSerializer):
    dispatcher = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        exclude = ()

    def get_dispatcher(self, obj: Channel) -> str:
        return fqn(obj.dispatcher)


class EventSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        exclude = ()

    def get_url(self, obj: "Event") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:event-detail",
                args=[
                    kwargs["parent_lookup_application__project__organization__slug"],
                    kwargs["parent_lookup_application__project__slug"],
                    kwargs["parent_lookup_application__slug"],
                    obj.slug,
                ],
            )
        )
