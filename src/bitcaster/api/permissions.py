import logging
from typing import TYPE_CHECKING, Optional, Tuple

from rest_framework import authentication, permissions
from rest_framework.request import Request

from bitcaster.auth.constants import Grant
from bitcaster.models import ApiKey, User

if TYPE_CHECKING:
    from bitcaster.api.base import SecurityMixin
    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import ApiRequest

logger = logging.getLogger(__name__)


class ApiKeyAuthentication(authentication.TokenAuthentication):
    keyword = "Key"
    model = ApiKey

    def authenticate(self, request: "ApiRequest") -> "Optional[Tuple[ApiKey, User]]":
        certs: "Optional[Tuple[ApiKey, User]]" = super().authenticate(request)
        if certs:
            request.user = certs[1]
        return certs


class ApiBasePermission(permissions.BasePermission):
    def _check_valid_scope(self, token: "ApiKey", view: "SecurityMixin") -> bool:
        if Grant.FULL_ACCESS in token.grants:
            return True
        ret = bool(len({*token.grants} & {*view.grants}))
        if not ret:
            logger.error(f"{view.grants} not in {token.grants}")
        return ret


class ApiApplicationPermission(ApiBasePermission):
    def has_permission(self, request: Request, view: "SecurityMixin") -> bool:
        if getattr(request, "auth", None) is None:
            return False
        # if not request.auth.application:
        #     return False
        #     if hasattr(request, "user") and not request.user.is_authenticated:
        # return False
        # if request.auth.application.slug != view.kwargs["app"]:
        #     return False
        return self._check_valid_scope(request.auth, view)

    def has_object_permission(self, request: Request, view: "SecurityMixin", obj: "AnyModel") -> bool:
        if getattr(request, "auth", None) is None:
            return False
        # if obj.application == request.auth.application:
        return self._check_valid_scope(request.auth, view)
