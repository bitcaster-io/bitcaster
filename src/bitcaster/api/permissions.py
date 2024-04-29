from typing import TYPE_CHECKING, Optional

from rest_framework import authentication, permissions
from rest_framework.request import Request

from bitcaster.auth.constants import Grant
from bitcaster.models import ApiKey, User

if TYPE_CHECKING:
    from bitcaster.api.base import SecurityMixin
    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import ApiRequest


class ApiKeyAuthentication(authentication.TokenAuthentication):
    keyword = "Key"
    model = ApiKey

    def authenticate(self, request: "ApiRequest") -> "Optional[list[ApiKey, User]]":
        certs: "Optional[list[ApiKey, User]]" = super().authenticate(request)
        if certs:
            # request.token = certs[0]
            request.user = certs[1]
        return certs


class ApiBasePermission(permissions.BasePermission):
    def _check_valid_scope(self, token: "ApiKey", view: "SecurityMixin"):
        if Grant.FULL_ACCESS in token.grants:
            return True
        return bool(len({*token.grants} & {*view.grants}))

    def has_permission(self, request: Request, view: "SecurityMixin") -> bool:
        if hasattr(request, "user") and not request.user.is_authenticated:
            return False
        if request.auth:
            return self._check_valid_scope(request.auth, view)
        return False

    # def has_object_permission(self, request: Request, view: "SecurityMixin", obj: "AnyModel") -> bool:
    #     if not request.user.is_authenticated:
    #         return False
    #     # if request.auth and Grant.EVENT_TRIGGER not in request.auth.grants:
    #     #     return False
    #     if not self._check_valid_scope(request.auth, view):
    #         return False
    #     if request.auth.application:
    #         scope = request.auth.application
    #         if isinstance(obj, Application):
    #             return obj == scope
    #         if hasattr(obj, "application") and obj.application:
    #             return obj.application == scope
    #
    #     elif request.auth.project:
    #         scope = request.auth.project
    #     elif request.auth.organization:
    #         scope = request.auth.organization
    #         if isinstance(obj, Organization):
    #             return obj == scope
    #         if hasattr(obj, "organization") and obj.organization:
    #             return obj.organization == scope
    #     else:
    #         raise ValueError()  # pragma: no cover
    #     # breakpoint()
    #     # if hasattr(obj, "application") and obj.application:
    #     #     return obj.application == request.auth.application
    #     # elif hasattr(obj, "project") and obj.project:
    #     #     return obj.project == request.auth.project
    #     # elif hasattr(obj, "organization") and obj.organization:
    #     #     return obj.organization == request.auth.organization
    #     # elif isinstance(obj, Application) and request.auth.application:
    #     #     return obj == request.auth.application
    #     # elif isinstance(obj, Project) and request.auth.project:
    #     #     return obj == request.auth.project
    #     # elif isinstance(obj, Organization) and request.auth.organization:
    #     #     return obj == request.auth.organization
    #
    #     # if isinstance(obj, (Organization, Project, Application)):
    #     #     return obj == scope
    #     #
    #     return False


class ApiOrgPermission(ApiBasePermission):
    pass


class ApiProjectPermission(ApiBasePermission):
    pass


class ApiApplicationPermission(ApiBasePermission):
    def has_permission(self, request: Request, view: "SecurityMixin") -> bool:
        if not request.auth:
            return False
        if not request.auth.application:
            return False
        if hasattr(request, "user") and not request.user.is_authenticated:
            return False
        return self._check_valid_scope(request.auth, view)

    def has_object_permission(self, request: Request, view: "SecurityMixin", obj: "AnyModel") -> bool:
        if not request.auth:
            return False
        if obj.application == request.auth.application:
            return self._check_valid_scope(request.auth, view)
        return False


#
# class ScopePermission(permissions.BasePermission):
#
#     def _check_valid_scope(self, token, view):
#         if Scopes.FULL_ACCESS in token.scopes:
#             return True
#         return bool(len({*token.scopes} & {*view.scopes}))
#
#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False
#         if hasattr(request, "token") and request.token:
#             if "organization__slug" in view.kwargs:
#                 org_slug = view.kwargs["organization__slug"]
#             else:  # 'slug' in view.kwargs:
#                 org_slug = view.kwargs["slug"]
#             org = Organization.objects.get(slug=org_slug)
#             return request.token.organization == org and self._check_valid_scope(request.token, view)
#
#         return None
#
#     def has_object_permission(self, request, view, obj):
#         if hasattr(request, "token") and request.token:
#             if isinstance(obj, Organization):
#                 if request.token.organization:
#                     return request.token.organization == obj
#                 else:
#                     return request.user.has_perm("*", obj)
#                     # return request.user.has_perm('manage_organization', obj)
#             elif isinstance(obj, Organization):
#                 return request.token.organization == obj
#         return True
#         # return request.user.has_perm('*', obj)
