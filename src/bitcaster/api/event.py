from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from bitcaster.models import Application

from ..auth.constants import Grant
from ..exceptions import InactiveError, LockError
from ..models import Event, Occurrence, User
from ..utils.filtering import validate_filters, validate_lookups, validate_schema
from .base import SecurityMixin

if TYPE_CHECKING:
    from rest_framework.request import Request

    from ..models.occurrence import OccurrenceOptions
    from ..types.filtering import QuerysetFilter
    from ..types.json import JSON

app_name = "api"


class OptionSerializer(serializers.Serializer):
    limit_to = serializers.ListField(child=serializers.CharField(), required=False)
    channels = serializers.ListField(child=serializers.CharField(), required=False)
    environs = serializers.ListField(child=serializers.CharField(), required=False)
    filters = serializers.JSONField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        unknown = set(self.parent.initial_data["options"]) - set(self.fields)
        if unknown:
            raise serializers.ValidationError("Unknown field(s): {}".format(", ".join(unknown)))
        return attrs

    def validate_filters(self, data: "dict") -> "QuerysetFilter":
        try:
            validate_schema(data)
            validate_filters(User.objects, data)
            validate_lookups(User, data)
            return data
        except DjangoValidationError as e:
            raise serializers.ValidationError({"error": e.message}) from None


class ActionSerializer(serializers.Serializer):
    context = serializers.DictField(required=False)
    options = OptionSerializer(required=False)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventList(SecurityMixin, ListAPIView):
    """List application events."""

    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_LIST]

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )


class EventTrigger(SecurityMixin, GenericAPIView):
    """Trigger application's event."""

    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_TRIGGER]
    parser = (JSONParser,)
    http_method_names = ["post"]

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.select_related("application__project__organization").filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )

    def post(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        ser = ActionSerializer(data=request.data)
        correlation_id = request.query_params.get("cid", None)

        if ser.is_valid():
            slug = self.kwargs["evt"]
            try:
                data: "JSON" = {}
                try:
                    evt: "Event" = self.get_queryset().get(slug=slug)
                except Event.DoesNotExist:
                    grant = Grant.EVENT_AUTO_CREATE in request.auth.grants
                    if grant and (
                        app := Application.objects.select_related("project__organization")
                        .filter(
                            project__organization__slug=self.kwargs["org"],
                            project__slug=self.kwargs["prj"],
                            slug=self.kwargs["app"],
                            auto_crete_event=True,
                        )
                        .first()
                    ):
                        slug = self.kwargs["evt"]
                        evt = Event.objects.create(
                            application=app,
                            active=False,
                            paused=True,
                            slug=slug,
                            name=f"AUTO: {slug.title()}",
                            description="auto created via APO invocation",
                        )
                        data["warning"] = f"New event '{evt.name}' created with id {evt.id}"
                    else:
                        raise
                if evt.locked:
                    raise LockError(evt)
                if evt.application.locked:
                    raise LockError(evt.application)
                if evt.application.project.locked:
                    raise LockError(evt.application.project)
                self.check_object_permissions(self.request, evt)
                opts: OccurrenceOptions = ser.validated_data.get("options", {})
                if request.auth.environments:
                    if "environs" in opts:
                        opts["environs"] = list(set(opts["environs"]).intersection(request.auth.environments))
                    else:
                        opts["environs"] = request.auth.environments
                o: "Occurrence" = evt.trigger(
                    context=ser.validated_data.get("context", {}),
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
                return Response({"warning": str(e)}, status=200)
            except Event.DoesNotExist:
                return Response({"error": f"Event not found {self.kwargs}"}, status=404)
        else:
            return Response(ser.errors, status=400)
