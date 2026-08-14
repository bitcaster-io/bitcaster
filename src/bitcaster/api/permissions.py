from typing import TYPE_CHECKING

import logging

from rest_framework import authentication, permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from ..auth.constants import Grant
from ..exceptions import InvalidGrantError
from ..models import ApiKey, User
from ..models.key import KeyKind

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import Model


class ApiKeyAuthentication(authentication.TokenAuthentication):
    keyword = "Key"
    model = ApiKey

    def authenticate(self, request: "Request") -> "tuple[ApiKey, User] | None":
        certs: "tuple[ApiKey, User] | None" = super().authenticate(request)
        if certs:
            request.user = certs[1]
        return certs


class ApiBasePermission(permissions.BasePermission):
    def _check_public_key(self, request: "Request", token: "ApiKey") -> bool:
        if token.kind != KeyKind.PUBLIC:
            return True
        if token.grants != [Grant.EVENT_TRIGGER]:
            raise InvalidGrantError(f"Public keys can only trigger events ({token})")
        if not token.application_id:
            raise InvalidGrantError(f"Public key not enabled for application scope ({token})")
        origin = request.headers.get("Origin", "")
        if not origin or origin not in (token.origins or []):
            raise InvalidGrantError(f"Origin not allowed for {token}")
        return True

    def _check_valid_scope(self, token: "ApiKey", view: "APIView") -> bool:
        if "org" in view.kwargs and view.kwargs["org"] != token.organization.slug:
            raise InvalidGrantError(f"Invalid organization for {token}")
        if "prj" in view.kwargs:
            if not token.project:
                raise InvalidGrantError("Key not enabled for project scope")
            if view.kwargs["prj"] != token.project.slug:
                raise InvalidGrantError(f"Invalid project for {token}")

        if "app" in view.kwargs:
            if not token.application:
                raise InvalidGrantError("Key not enabled for application scope")
            if view.kwargs["app"] != token.application.slug:
                raise InvalidGrantError(f"Invalid application for {token}")

        if Grant.FULL_ACCESS in token.grants:
            return True
        ret = bool(len({*token.grants} & {*view.grants}))
        if not ret:
            logger.error(f"{view.grants} not in {token.grants}")
            raise InvalidGrantError(f"You do not have permission to perform this action. {view.grants}")
        return ret


class ApiApplicationPermission(ApiBasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        if getattr(request, "auth", None) is None:
            return (
                getattr(request, "user", None) is not None
                and request.user.is_authenticated
                and request.user.is_superuser
            )
        return (
            isinstance(request.auth, ApiKey)
            and self._check_valid_scope(request.auth, view)
            and self._check_public_key(request, request.auth)
        )

    def has_object_permission(self, request: Request, view: "APIView", obj: "Model") -> bool:
        if getattr(request, "auth", None) is None:
            return (
                getattr(request, "user", None) is not None
                and request.user.is_authenticated
                and request.user.is_superuser
            )
        return (
            isinstance(request.auth, ApiKey)
            and self._check_valid_scope(request.auth, view)
            and self._check_public_key(request, request.auth)
        )
