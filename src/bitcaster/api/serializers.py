from django.db.models import Model
from django.utils.functional import cached_property
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from strategy_field.utils import fqn

from bitcaster.models import Application, Channel, Event, Organization, Project, User
from bitcaster.utils.http import absolute_uri


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")


class SelecteOrganizationSerializer(serializers.ModelSerializer):
    # co_key = "parent_lookup_organization__slug"
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


class OrganizationSerializer(serializers.ModelSerializer):
    owner = serializers.EmailField(source="owner.email", read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="api:organization-detail", lookup_field="slug", read_only=True)

    # hyperlinks
    links = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("id", "slug", "owner", "name", "links", "url")
        # read_only_fields = ("id", "slug", "status", "members", "links")

    def get_links(self, obj):
        return {
            # "members": absolute_uri(reverse("api:member-list", args=[obj.slug])),
            "channels": absolute_uri(reverse("api:org-channel-list", args=[obj.slug])),
            "projects": absolute_uri(reverse("api:org-project-list", args=[obj.slug])),
            # "addresses": absolute_uri(reverse("api:address-list", args=[obj.slug])),
        }


class ProjectSerializer(SelecteOrganizationSerializer):
    co_key = "parent_lookup_organization__slug"
    url = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    # applications = serializers.SerializerMethodField()
    # channels = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("url", "name", "slug", "organization", "links")

    def get_url(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:org-project-detail",
                args=[kwargs["parent_lookup_organization__slug"], obj.slug],
            )
        )

    def get_links(self, obj):
        kwargs = self.context["view"].kwargs
        return {
            # "members": absolute_uri(reverse("api:member-list", args=[obj.slug])),
            "applications": absolute_uri(
                reverse("api:prj-application-list", args=[kwargs["parent_lookup_organization__slug"], obj.slug])
            ),
            "channels": absolute_uri(
                reverse("api:prj-channel-list", args=[kwargs["parent_lookup_organization__slug"], obj.slug])
            ),
            # "projects": absolute_uri(reverse("api:org-project-list", args=[obj.slug])),
            # "addresses": absolute_uri(reverse("api:address-list", args=[obj.slug])),
        }

    #
    # def get_applications(self, obj: "Project") -> str:
    #     kwargs = self.context["view"].kwargs
    #     return self.context["request"].build_absolute_uri(
    #         reverse(
    #             "api:prj-application-list",
    #             args=[kwargs["parent_lookup_organization__slug"], obj.slug],
    #         )
    #     )
    #
    # def get_channels(self, obj: "Project") -> str:
    #     kwargs = self.context["view"].kwargs
    #     return self.context["request"].build_absolute_uri(
    #         reverse(
    #             "api:prj-channel-list",
    #             args=[
    #                 kwargs["parent_lookup_organization__slug"],
    #                 obj.slug,
    #             ],
    #         )
    #     )


class ApplicationSerializer(SelecteOrganizationSerializer):
    co_key = "parent_lookup_project__organization__slug"
    url = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ("name", "url", "events")

    def get_url(self, obj: "Project") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:prj-application-detail",
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
                "api:app-event-list",
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
    channels = serializers.SerializerMethodField()
    trigger_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        exclude = (
            "id",
            "application",
        )

    def get_channels(self, obj: "Event") -> list[str]:
        return [ch.name for ch in obj.channels.all()]

    def get_trigger_url(self, obj: "Event") -> str:
        return absolute_uri(
            reverse(
                "api:trigger-trigger",
                args=[
                    obj.application.project.organization.slug,
                    obj.application.project.slug,
                    obj.application.slug,
                    obj.slug,
                ],
            )
        )

    def get_url(self, obj: "Event") -> str:
        kwargs = self.context["view"].kwargs
        return self.context["request"].build_absolute_uri(
            reverse(
                "api:app-event-detail",
                args=[
                    kwargs["parent_lookup_application__project__organization__slug"],
                    kwargs["parent_lookup_application__project__slug"],
                    kwargs["parent_lookup_application__slug"],
                    obj.slug,
                ],
            )
        )
