from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.request import Request
from rest_framework.response import Response

from bitcaster.models import Event, Occurrence

from ..auth.constants import Grant
from .base import BaseModelViewSet
from .permissions import ApiKeyAuthentication


class TriggerSerializer(serializers.HyperlinkedModelSerializer):
    url = HyperlinkedIdentityField(view_name="api:trigger-detail", lookup_field="slug")

    class Meta:
        model = Event
        read_only_fields = fields = ("id", "name", "slug", "description", "url")
        lookup_field = "slug"


class ActionSerializer(serializers.Serializer):
    context = serializers.DictField(required=False)
    options = serializers.DictField(required=False)


class EventViewSet(BaseModelViewSet):
    pass


class TriggerViewSet(BaseModelViewSet):
    queryset = Event.objects.all().order_by("-pk")
    serializer_class = TriggerSerializer
    required_grants = (Grant.EVENT_TRIGGER,)
    parser = (JSONParser,)
    lookup_field = "slug"

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=ActionSerializer,
        authentication_classes=[
            ApiKeyAuthentication,
        ],
        url_path=r"o/(?P<org>.+)/p/(?P<prj>.+)/a/(?P<app>.+)/e/(?P<event>.+)",
    )
    def trigger(self, request: "Request", org: str, prj: str, app: str, event: str) -> Response:
        ser = ActionSerializer(data=request.data)
        correlation_id = request.query_params.get("cid", None)
        if ser.is_valid():
            try:
                obj: "Event" = Event.objects.get(
                    application__project__organization__slug=org,
                    application__project__slug=prj,
                    application__slug=app,
                    slug=event,
                )
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
