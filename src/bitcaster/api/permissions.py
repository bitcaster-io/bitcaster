import logging
from typing import TYPE_CHECKING

from rest_framework import authentication, permissions
from rest_framework.request import Request

from bitcaster.auth.constants import Grant
from bitcaster.exceptions import InvalidGrantError
from bitcaster.models import ApiKey, User

if TYPE_CHECKING:
    from bitcaster.api.base import SecurityMixin
    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import ApiRequest

logger = logging.getLogger(__name__)


class ApiKeyAuthentication(authentication.TokenAuthentication):
    keyword = "Key"
    model = ApiKey

    def authenticate(self, request: "ApiRequest") -> "tuple[ApiKey, User] | None":
        certs: "tuple[ApiKey, User] | None" = super().authenticate(request)
        if certs:
            request.user = certs[1]
        return certs


class ApiBasePermission(permissions.BasePermission):
    def _check_valid_scope(self, token: "ApiKey", view: "SecurityMixin") -> bool:
        if "org" in view.kwargs and view.kwargs["org"] != token.organization.slug:
            raise InvalidGrantError(f"Invalid organization for {token}")
        if "prj" in view.kwargs:
            if not token.project:
                raise InvalidGrantError("Key not enabled form project scope")
            if view.kwargs["prj"] != token.project.slug:
                raise InvalidGrantError(f"Invalid project for {token}")

        if "app" in view.kwargs:
            if not token.application:
                raise InvalidGrantError("Key not enabled form application scope")
            if view.kwargs["app"] != token.application.slug:
                raise InvalidGrantError(f"Invalid application for {token}")

        if Grant.FULL_ACCESS in token.grants:
            return True
        ret = bool(len({*token.grants} & {*view.grants}))
        if not ret:
            logger.error(f"{view.grants} not in {token.grants}")
        return ret


class ApiApplicationPermission(ApiBasePermission):
    def has_permission(self, request: Request, view: "SecurityMixin") -> bool:
        if getattr(request, "auth", None) is None:
            if getattr(request, "user", None) is not None:
                if request.user.is_authenticated and request.user.is_superuser:
                    return True
            return False
        return self._check_valid_scope(request.auth, view)

    def has_object_permission(self, request: Request, view: "SecurityMixin", obj: "AnyModel") -> bool:
        if getattr(request, "auth", None) is None:
            if getattr(request, "user", None) is not None:
                if request.user.is_authenticated and request.user.is_superuser:
                    return True
            return False
        return self._check_valid_scope(request.auth, view)
