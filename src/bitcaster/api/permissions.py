from rest_framework import authentication, permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from bitcaster.auth.constants import Grant
from bitcaster.models import ApiKey, Event


class ApiKeyAuthentication(authentication.TokenAuthentication):
    keyword = "ApiKey"
    model = ApiKey


class TriggerPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.auth:
            return Grant.EVENT_TRIGGER in request.auth.grants
        return False

    def has_object_permission(self, request: Request, view: APIView, obj: Event) -> bool:
        if request.auth:
            return Grant.EVENT_TRIGGER in request.auth.grants and obj.application == request.auth.application
        return False
