from typing import TYPE_CHECKING, Any

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from .base import BaseView
from ..auth.constants import Grant
from ..constants import bitcaster
from ..models import (
    Address,
    Application,
    ApplicationMembership,
    Assignment,
    Channel,
    DistributionList,
    User,
    UserRole,
)
from ..models.address import PROTOCOL_TO_ADDRESS
from ..utils.json import JsonUpdateMode, process_dict

if TYPE_CHECKING:
    from ..constants import AddressType


class RegisterAddressSerializer(serializers.Serializer[Any]):
    value = serializers.CharField(required=True)
    name = serializers.CharField(required=False, allow_blank=True, default="")
    assign_to_preferred_channel = serializers.BooleanField(required=False, default=False)


class RegisterMembershipSerializer(serializers.Serializer[Any]):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    custom_fields = serializers.DictField(required=False)
    active = serializers.BooleanField(required=False, default=True)
    addresses = RegisterAddressSerializer(many=True, required=False, default=list)
    distribution_list = serializers.CharField(required=False, allow_null=True, default=None)


class ApplicationRegisterView(BaseView):
    """Register a User as Application Member of the application in the URL path."""

    required_grants = [Grant.MANAGE_APPLICATION_USERS]

    @extend_schema(
        request=RegisterMembershipSerializer,
        responses={
            200: inline_serializer(name="RegisterMembershipResponse", fields={"created": serializers.BooleanField()})
        },
        description=_(
            "Register a user as member of the application. Creates the user if needed, "
            "stores per-application custom fields, creates addresses, assigns them to "
            "preferred channels and optionally adds the assignments to a distribution list."
        ),
    )
    def post(self, request: Request, org: str, prj: str, app: str) -> Response:
        application = get_object_or_404(Application, slug=app, project__slug=prj, project__organization__slug=org)
        serializer = RegisterMembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        distribution_list: DistributionList | None = None
        if dl_name := data["distribution_list"]:
            distribution_list = DistributionList.objects.filter(name=dl_name, project=application.project).first()
            if distribution_list is None:
                return Response(
                    {"distribution_list": f"DistributionList '{dl_name}' does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if distribution_list.application_id and distribution_list.application_id != application.pk:
                return Response(
                    {"distribution_list": f"DistributionList '{dl_name}' is pinned to another application"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                },
            )
            UserRole.objects.get_or_create(
                user=user, organization=application.project.organization, group=bitcaster.get_default_group()
            )
            membership, __ = ApplicationMembership.objects.get_or_create(
                user=user, application=application, defaults={"active": data["active"]}
            )
            membership.active = data["active"]
            if custom_fields := data.get("custom_fields"):
                membership.custom_fields = process_dict(membership.custom_fields, custom_fields, JsonUpdateMode.MERGE)
            membership.save()

            addresses: list[dict[str, Any]] = []
            assignments: list[dict[str, Any]] = []
            recipients: list[Assignment] = []
            for entry in data["addresses"]:
                address_type: "AddressType" = Address.objects.get_type_from_value(entry["value"])
                name = entry["name"] or address_type.lower()
                address, _ = Address.objects.get_or_create(user=user, value=entry["value"], name=name)
                addresses.append({"value": address.value, "name": address.name, "type": address.type})
                if not entry["assign_to_preferred_channel"]:
                    continue
                channels = self._get_preferred_channels(application, address.type)
                if not channels:
                    assignments.append({"address": address.value, "channel": None, "skipped": True})
                    continue
                for channel in channels:
                    assignment, __ = Assignment.objects.get_or_create(
                        address=address, channel=channel, defaults={"validated": True, "active": True}
                    )
                    recipients.append(assignment)
                    assignments.append(
                        {"address": address.value, "channel": channel.name, "protocol": channel.protocol}
                    )

            recipients_added = 0
            if distribution_list and recipients:
                existing = set(
                    distribution_list.recipients.filter(pk__in=[a.pk for a in recipients]).values_list("pk", flat=True)
                )
                distribution_list.recipients.add(*recipients)
                recipients_added = len({a.pk for a in recipients} - existing)

        return Response(
            {
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                },
                "created": created,
                "membership": {
                    "custom_fields": membership.custom_fields,
                    "active": membership.active,
                    "locked": membership.locked,
                    "enable_notifications": membership.enable_notifications,
                },
                "addresses": addresses,
                "assignments": assignments,
                "distribution_list": (
                    {"name": distribution_list.name, "recipients_added": recipients_added}
                    if distribution_list
                    else None
                ),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def _get_preferred_channels(self, application: Application, address_type: str) -> list[Channel]:
        """Preferred channels compatible with the address type; project-level overrides org-level per protocol."""
        compatible = [protocol for protocol, a_type in PROTOCOL_TO_ADDRESS.items() if a_type == address_type]
        selected: dict[str, Channel] = {}
        candidates = Channel.objects.active().filter(
            Q(project=application.project) | Q(project__isnull=True),
            organization=application.project.organization,
            preferred=True,
            protocol__in=compatible,
        )
        for channel in sorted(candidates, key=lambda ch: ch.project_id is not None):
            selected[channel.protocol] = channel
        return list(selected.values())
