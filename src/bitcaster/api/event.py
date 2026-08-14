from typing import TYPE_CHECKING, Any

import json

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from .base import SecurityMixin
from ..auth.constants import Grant
from ..exceptions import InactiveError, InvalidGrantError, LockError
from ..models import ApiKey, Application, ClientToken, Event, LogEntry, Occurrence, User
from ..utils.filtering import validate_filters, validate_lookups, validate_schema

if TYPE_CHECKING:
    from rest_framework.request import Request

    from ..models.occurrence import OccurrenceOptions
    from ..types.filtering import QuerysetFilter
    from ..types.json import JSONValue

app_name = "api"


class OptionSerializer(serializers.Serializer[Any]):
    limit_to = serializers.ListField(child=serializers.CharField(), required=False)
    channels = serializers.ListField(child=serializers.CharField(), required=False)
    environs = serializers.ListField(child=serializers.CharField(), required=False)
    filters = serializers.JSONField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if "options" in self.parent.initial_data:
            unknown = set(self.parent.initial_data["options"]) - set(self.fields)
            if unknown:
                raise serializers.ValidationError("Unknown field(s): {}".format(", ".join(unknown)))
        return attrs

    def validate_filters(self, data: "QuerysetFilter") -> "QuerysetFilter":
        try:
            validate_schema(data)
            validate_filters(User.objects, data)
            validate_lookups(User, data)
            return data
        except DjangoValidationError as e:
            raise serializers.ValidationError({"error": e.message}) from None


class ActionSerializer(serializers.Serializer[dict[str, Any]]):
    payload_context = serializers.DictField(required=False)
    options = OptionSerializer(required=False)

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        if isinstance(data, dict) and "context" in data:
            data = data.copy()
            data["payload_context"] = data.pop("context")
        return super().to_internal_value(data)


class EventSerializer(serializers.ModelSerializer[Event]):
    class Meta:
        model = Event
        fields = "__all__"


class EventList(SecurityMixin, ListAPIView[Event]):
    """List application events."""

    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_LIST]

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )

    @extend_schema(
        responses={200: EventSerializer(many=True)},
        description=_("List all events configured for a specific application."),
    )
    def get(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class EventTrigger(SecurityMixin, GenericAPIView[Event]):
    """Trigger application's event."""

    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_TRIGGER, Grant.WEB_TRIGGER]
    parser = (JSONParser,)
    http_method_names = ["post"]

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.select_related("application__project__organization").filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )

    @staticmethod
    def _is_web_credential(request: "Request") -> bool:
        auth = getattr(request, "auth", None)
        if isinstance(auth, ClientToken):
            return True
        if isinstance(auth, ApiKey):
            return auth.is_web()
        return False

    def _check_web_restrictions(self, request: "Request", ser: ActionSerializer) -> Response | None:
        if not self._is_web_credential(request):
            return None
        initial_options = ser.initial_data.get("options") or {}
        if "filters" in initial_options:
            return Response({"error": "filters are not allowed for web credentials"}, status=400)
        context = ser.validated_data.get("payload_context", {})
        if len(json.dumps(context).encode("utf-8")) > settings.TRIGGER_CONTEXT_MAX_SIZE:
            return Response(
                {"error": f"context exceeds the maximum size of {settings.TRIGGER_CONTEXT_MAX_SIZE} bytes"},
                status=400,
            )
        return None

    @extend_schema(
        request=ActionSerializer,
        responses={201: Any},
        description=_(
            "Trigger a specific event. "
            "This endpoint accepts a payload context and routing options. "
            "If configured, it may auto-create the event if it doesn't exist."
        ),
    )
    def post(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        ser = ActionSerializer(data=request.data)
        correlation_id = request.query_params.get("cid", None)

        if ser.is_valid():
            slug = self.kwargs["evt"]
            create_occurrence = True
            try:
                data: dict[str, "JSONValue"] = {}
                try:
                    evt: "Event" = self.get_queryset().get(slug=slug)
                    if not evt.active:
                        raise InactiveError(evt)
                except Event.DoesNotExist:
                    grant = not self._is_web_credential(request) and Grant.EVENT_AUTO_CREATE in request.auth.grants
                    if grant and (
                        app := Application.objects.select_related("project__organization")
                        .filter(
                            project__organization__slug=self.kwargs["org"],
                            project__slug=self.kwargs["prj"],
                            slug=self.kwargs["app"],
                            auto_create_event=True,
                        )
                        .first()
                    ):
                        slug = self.kwargs["evt"]
                        match app.auto_create_options:
                            case Application.AutoCreateOption.PROCESS:
                                paused = False
                                active = True
                                create_occurrence = True
                            case Application.AutoCreateOption.PAUSED:
                                paused = True
                                active = True
                                create_occurrence = True
                            case Application.AutoCreateOption.DUMMY:
                                paused = False
                                active = True
                                create_occurrence = False
                            case _:  ## Application.AutoCreateOption.INACTIVE
                                paused = False
                                active = False
                                create_occurrence = False

                        evt = Event.objects.create(
                            application=app,
                            active=active,
                            paused=paused,
                            slug=slug,
                            name=f"AUTO: {slug.title()}",
                            description="auto created via API invocation",
                        )
                        LogEntry.objects.log_system_action(
                            evt,
                            LogEntry.ADDITION,
                            "auto created via API invocation",
                        )
                        data["warning"] = f"New event '{evt.name}' created with id {evt.id}"
                        data["creation_op   tions"] = str(Application.AutoCreateOption(app.auto_create_options).label)
                        data["status"] = {"paused": evt.paused, "active": evt.active, "trigger": create_occurrence}
                    else:
                        raise
                if evt.locked:
                    raise LockError(evt)
                if evt.application.locked:
                    raise LockError(evt.application)
                if evt.application.project.locked:
                    raise LockError(evt.application.project)
                self.check_object_permissions(self.request, evt)

                if isinstance(request.auth, ClientToken) and request.auth.event and request.auth.event_id != evt.pk:
                    raise InvalidGrantError("Token is not valid for this event")

                if restriction := self._check_web_restrictions(request, ser):
                    return restriction

                opts: "OccurrenceOptions" = ser.validated_data.get("options", {})
                if environments := getattr(request.auth, "environments", None):
                    if "environs" in opts:
                        opts["environs"] = list(set(opts["environs"]).intersection(environments))
                    else:
                        opts["environs"] = environments
                if create_occurrence:
                    o: "Occurrence" = evt.trigger(
                        context=ser.validated_data.get("payload_context", {}),
                        options=opts,
                        cid=correlation_id,
                    )
                    data["occurrence"] = o.pk
                    if o.event.paused or o.event.application.paused:
                        data["paused"] = True
                return Response(data, status=201)
            except LockError as e:
                return Response({"error": str(e)}, status=400)
            except InactiveError as e:
                return Response({"error": str(e)}, status=400)
            except Event.DoesNotExist:
                return Response({"error": f"Event not found {self.kwargs}"}, status=404)
        else:
            return Response(ser.errors, status=400)
