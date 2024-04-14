from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from bitcaster.api.permissions import TriggerPermission, ApiKeyAuthentication
from bitcaster.models import Event


class TriggerSerializer(serializers.HyperlinkedModelSerializer):
    url = HyperlinkedIdentityField(view_name="api:trigger-detail", lookup_field="slug")

    class Meta:
        model = Event
        read_only_fields = fields = ("id", "name", "slug", "description", "url")
        lookup_field = "slug"


class ActionSerializer(serializers.Serializer):
    context = serializers.DictField()


class TriggerViewSet(ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by("-pk")
    serializer_class = TriggerSerializer
    permission_classes = [TriggerPermission]
    authentication_classes = [ApiKeyAuthentication, SessionAuthentication]

    lookup_field = "slug"

    @action(detail=True, methods=["GET"], serializer_class=ActionSerializer)
    def trigger(self, request: "HttpRequest", *args, **kwargs):
        return Response(request.POST)

    # def list(self, request, format=None):
    #     # latest_publish = Publish.objects.latest('created_time')
    #     # latest_meeting = Meeting.objects.latest('created_time')
    #     # latest_training = Training.objects.latest('created_time')
    #     # latest_exhibiting = Exhibiting.objects.latest('created_time')
    #
    #     return Response(
    #         {
    #             "publish_updatetime": 1,
    #             "meeting_updatetime": 2,
    #             "training_updatetime": 3,
    #             "exhibiting_updatetime": 3,
    #         }
    #     )
