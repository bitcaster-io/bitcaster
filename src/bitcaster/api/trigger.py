from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from bitcaster.api.permissions import ApiKeyAuthentication, TriggerPermission
from bitcaster.models import Event


class TriggerSerializer(serializers.HyperlinkedModelSerializer):
    url = HyperlinkedIdentityField(view_name="api:trigger-detail", lookup_field="slug")

    class Meta:
        model = Event
        read_only_fields = fields = ("id", "name", "slug", "description", "url")
        lookup_field = "slug"


class ActionSerializer(serializers.Serializer):
    context = serializers.DictField(required=True)


class TriggerViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by("-pk")
    serializer_class = TriggerSerializer
    permission_classes = [TriggerPermission]
    authentication_classes = [ApiKeyAuthentication, SessionAuthentication]

    lookup_field = "slug"

    @action(
        detail=True,
        methods=["GET", "POST"],
        serializer_class=ActionSerializer,
        authentication_classes=[
            ApiKeyAuthentication,
        ],
    )
    def trigger(self, request: "Request") -> Response:
        if request.method == "POST":
            ser = ActionSerializer(data=request.data)
            if ser.is_valid():
                obj: "Event" = Event.objects.get(slug=self.kwargs["slug"])
                self.check_object_permissions(self.request, obj)
                obj.trigger(ser.validated_data["context"])
                return Response(ser.data)
            else:
                return Response(ser.errors, status=400)

        return Response({})
