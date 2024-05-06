from django.urls import path
from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from ..auth.constants import Grant
from ..models import Event, Occurrence
from .base import SecurityMixin
from .system import PingView
from .trigger import ActionSerializer

app_name = "api"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventList(SecurityMixin, ListAPIView):
    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_LIST]

    def get_queryset(self):
        return Event.objects.filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )


class EventTrigger(SecurityMixin, RetrieveAPIView):
    serializer_class = EventSerializer
    required_grants = [Grant.EVENT_TRIGGER]

    def get_queryset(self):
        return Event.objects.filter(
            application__project__organization__slug=self.kwargs["org"],
            application__project__slug=self.kwargs["prj"],
            application__slug=self.kwargs["app"],
        )

    # def post(self, request, *args, **kwargs):
    #     obj = self.get_queryset().get(slug=self.kwargs["evt"])
    #     return Response(EventSerializer(obj).data)

    def post(self, request: "Request", *args, **kwargs) -> Response:
        ser = ActionSerializer(data=request.data)
        correlation_id = request.query_params.get("cid", None)
        if ser.is_valid():
            try:
                obj: "Event" = self.get_queryset().get(slug=self.kwargs["evt"])
                self.check_object_permissions(self.request, obj)
                o: "Occurrence" = obj.trigger(
                    ser.validated_data.get("context", {}),
                    options=ser.validated_data.get("options", {}),
                    cid=correlation_id,
                )
                return Response({"occurrence": o.pk})
            except Event.DoesNotExist:
                return Response({"error": "Event not found"}, status=404)
        else:
            return Response(ser.errors, status=400)


urlpatterns = [
    path("system/ping/", PingView.as_view(), name="system-ping"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/", EventList.as_view(), name="event-list"),
    path("o/<slug:org>/p/<slug:prj>/a/<slug:app>/e/<slug:evt>/trigger/", EventTrigger.as_view(), name="event-trigger"),
]
