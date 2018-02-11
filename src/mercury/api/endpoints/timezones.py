import pytz
from rest_framework.response import Response

from mercury.api.endpoints.base import BaseViewSet


class TimezoneViewSet(BaseViewSet):
    http_method_names = ['get', ]

    def list(self, request):
        return Response(map(str, pytz.all_timezones))
