from typing import TYPE_CHECKING, Any

from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from ..auth.constants import Grant
from ..exceptions import LockError
from ..models import Event, Occurrence
from .base import SecurityMixin

if TYPE_CHECKING:
    from rest_framework.request import Request

    from ..models.occurrence import OccurrenceOptions

app_name = "api"


class OptionSerializer(serializers.Serializer):
    limit_to = serializers.ListField(child=serializers.CharField(), required=False)
    channels = serializers.ListField(child=serializers.CharField(), required=False)
    environs = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        unknown = set(self.parent.initial_data["options"]) - set(self.fields)
        if unknown:
            raise serializers.ValidationError("Unknown field(s): {}".format(", ".join(unknown)))
        return attrs


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
                evt: "Event" = self.get_queryset().get(slug=slug)
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
                return Response({"occurrence": o.pk}, status=201)
            except LockError as e:
                return Response({"error": str(e)}, status=400)
            except Event.DoesNotExist:
                return Response({"error": f"Event not found {self.kwargs}"}, status=404)
        else:
            return Response(ser.errors, status=400)
