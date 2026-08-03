from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from .base import BaseView
from ..auth.constants import Grant
from ..models import Assignment, Notification, Subscription


class SubscriptionSerializer(serializers.Serializer[Subscription]):
    assignment = serializers.IntegerField()
    active = serializers.BooleanField(required=False, default=True)


class NotificationSubscriptionView(BaseView):
    required_grants = [Grant.MANAGE_APPLICATION_USERS]

    def _get_notification(self, org: str, prj: str, app: str, notification_pk: int) -> Notification:
        return get_object_or_404(
            Notification,
            pk=notification_pk,
            event__application__slug=app,
            event__application__project__slug=prj,
            event__application__project__organization__slug=org,
        )

    def _get_assignment(self, pk: int, notification: Notification) -> Assignment:
        assignment = get_object_or_404(Assignment, pk=pk)
        # Ensure the assignment belongs to the same organization as the notification
        org_id = notification.event.application.project.organization_id
        if assignment.channel.organization_id != org_id:
            # Assignment exists but belongs to a different organization
            from django.http import Http404

            raise Http404
        return assignment

    def _parse_payload(self, request: Request) -> dict[str, Any]:
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def _get_assignment_from_params(self, request: Request) -> int:
        pk = request.query_params.get("assignment")
        if pk is None:
            raise serializers.ValidationError({"assignment": "This field is required."})
        try:
            return int(pk)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"assignment": "Must be an integer."}) from None

    @extend_schema(
        request=SubscriptionSerializer,
        responses={
            status.HTTP_201_CREATED: SubscriptionSerializer,
            status.HTTP_200_OK: SubscriptionSerializer,
        },
        description=_("Subscribe an assignment to a notification. Idempotent."),
    )
    def post(self, request: Request, org: str, prj: str, app: str, notification_pk: int) -> Response:
        notification = self._get_notification(org, prj, app, notification_pk)
        data = self._parse_payload(request)
        assignment = self._get_assignment(data["assignment"], notification)
        active = bool(data.get("active", True))
        subscription, created = Subscription.objects.get_or_create(
            notification=notification, assignment=assignment, defaults={"active": active}
        )
        if not created:
            subscription.active = active
            subscription.save()
        return Response(
            {"subscription": subscription.pk},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        parameters=[SubscriptionSerializer],
        responses={status.HTTP_200_OK: SubscriptionSerializer},
        description=_("Unsubscribe an assignment from a notification. Idempotent."),
    )
    def delete(self, request: Request, org: str, prj: str, app: str, notification_pk: int) -> Response:
        notification = self._get_notification(org, prj, app, notification_pk)
        assignment_pk = self._get_assignment_from_params(request)
        assignment = self._get_assignment(assignment_pk, notification)
        subscription = get_object_or_404(Subscription, notification=notification, assignment=assignment)
        if subscription.active:
            subscription.active = False
            subscription.save()
        return Response({"subscription": subscription.pk})
