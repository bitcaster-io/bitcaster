from django.conf import settings

from rest_framework.response import Response

from mercury.api.endpoints.base import BaseViewSet


class LanguageViewSet(BaseViewSet):
    http_method_names = ['get', ]

    def list(self, request):
        return Response([{"id": x, "text": y} for x, y in settings.LANGUAGES])
