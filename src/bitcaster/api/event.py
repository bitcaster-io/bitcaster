from typing import Any

from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response

from ..auth.constants import Grant
from ..models import Event, Occurrence
from .base import SecurityMixin

app_name = "api"


class ActionSerializer(serializers.Serializer):
    context = serializers.DictField(required=False)
    options = serializers.DictField(required=False)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventList(SecurityMixin, ListAPIView):
    """
    List application events
    """

    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_LIST]

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )


class EventTrigger(SecurityMixin, GenericAPIView):
    """
    Trigger application's event
    """

    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_TRIGGER]
    parser = (JSONParser,)
    http_method_names = ["post"]

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.filter(
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
                self.check_object_permissions(self.request, evt)
                o: "Occurrence" = evt.trigger(
                    ser.validated_data.get("context", {}),
                    options=ser.validated_data.get("options", {}),
                    cid=correlation_id,
                )
                return Response({"occurrence": o.pk}, status=201)
            except Event.DoesNotExist:
                return Response({"error": f"Event not found {self.kwargs}"}, status=404)
        else:
            return Response(ser.errors, status=400)
