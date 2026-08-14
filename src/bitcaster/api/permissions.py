from typing import TYPE_CHECKING

import logging

from rest_framework import authentication, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.views import APIView

from django.db.models import Q
from django.utils import timezone

from ..auth.constants import Grant
from ..exceptions import InvalidGrantError, InvalidOriginError
from ..models import ApiKey, ClientToken, User

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import Model

LAST_USED_UPDATE_INTERVAL = 60  # seconds


class ApiKeyAuthentication(authentication.TokenAuthentication):
    keyword = "Key"
    model = ApiKey

    def authenticate(self, request: "Request") -> "tuple[User, ApiKey | ClientToken] | None":
        certs: "tuple[User, ApiKey | ClientToken] | None" = super().authenticate(request)
        if certs:
            request.user = certs[0]
        return certs

    def authenticate_credentials(self, key: str) -> "tuple[User, ApiKey | ClientToken]":
        now = timezone.now()
        try:
            api_key = (
                ApiKey.objects.filter(key=key, is_active=True)
                .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
                .select_related("user")
                .get()
            )
        except ApiKey.DoesNotExist:
            try:
                client_token = (
                    ClientToken.objects.filter(token=key, is_active=True, expires_at__gt=now)
                    .select_related("user")
                    .get()
                )
            except ClientToken.DoesNotExist:
                raise AuthenticationFailed("Invalid token.") from None
            self._touch_last_used(client_token)
            return client_token.user, client_token
        self._touch_last_used(api_key)
        return api_key.user, api_key

    @staticmethod
    def _touch_last_used(credential: "ApiKey | ClientToken") -> None:
        now = timezone.now()
        if (
            credential.last_used_at is None
            or (now - credential.last_used_at).total_seconds() > LAST_USED_UPDATE_INTERVAL
        ):
            type(credential).objects.filter(pk=credential.pk).update(last_used_at=now)


def normalize_origin(origin: str) -> str:
    return origin.rstrip("/")


def check_origin(request: Request, credential: "ApiKey | ClientToken") -> bool:
    if isinstance(credential, ApiKey) and not credential.is_web():
        return True
    origin = request.META.get("HTTP_ORIGIN") or ""
    if not origin:
        raise InvalidOriginError("Origin header is required for web credentials")
    origin = normalize_origin(origin)
    if origin == "null" or origin not in {normalize_origin(o) for o in (credential.allowed_origins or []) if o}:
        raise InvalidOriginError("Origin not allowed")
    return True


class ApiBasePermission(permissions.BasePermission):
    def _check_valid_scope(self, token: "ApiKey | ClientToken", view: "APIView") -> bool:
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
        if not isinstance(request.auth, ApiKey | ClientToken):
            return False
        check_origin(request, request.auth)
        return self._check_valid_scope(request.auth, view)

    def has_object_permission(self, request: Request, view: "APIView", obj: "Model") -> bool:
        if getattr(request, "auth", None) is None:
            return (
                getattr(request, "user", None) is not None
                and request.user.is_authenticated
                and request.user.is_superuser
            )
        if not isinstance(request.auth, ApiKey | ClientToken):
            return False
        check_origin(request, request.auth)
        return self._check_valid_scope(request.auth, view)
