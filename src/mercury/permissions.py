# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from mercury.middleware import get_anonymous_user
from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           SessionAuthentication,
                                           get_authorization_header,)
from rest_framework.permissions import BasePermission, IsAuthenticated

from mercury.models import ApiAuthToken, Application, User
from mercury.utils.language import get_attr
from django.utils.translation import ugettext as _

class SameUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or (request.user == obj)



# class AppPermission(IsAuthenticated):
#     def has_permission(self, request, view):
#         return False
#
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_superuser or (request.user == obj.owner)


class IsApplicationRelated(IsAuthenticated):
    # def __init__(self, attr) -> None:
    #     super().__init__()
    #     self.attr = attr
    attr = None

    @classmethod
    def create(cls, attr):
        return type("-", (cls,), {'attr': attr})

    def has_permission(self, request, view):
        if 'application__pk' in view.kwargs:
            app = view.get_selected_application()
            return request.user.is_authenticated and request.user.is_admin(app)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        app = get_attr(obj, self.attr)
        return request.user.is_superuser or (request.user == app.owner)


class IsOwnerOrMaintainter(IsAuthenticated):
    def has_permission(self, request, view):
        if 'application__pk' in view.kwargs:
            app = Application.objects.get(pk=view.kwargs['application__pk'])
            return request.user.is_admin(app)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.user.is_superuser or
                obj.owner == request.user or
                obj.maintainers.filter(id=request.user.id).exists())


class IsOwner(IsAuthenticated):
    # def has_permission(self, request, view):
    #     return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or (request.user == obj.owner)


# class IsApplication(IsAuthenticated):
#     # def has_permission(self, request, view):
#     #     return request.user.is_authenticated()
#
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_superuser or (request.user.is_application)


# def detail_permission_factory(attr):
#     class AppPermission(IsAuthenticated):
#         attr = ''
#
#         def has_object_permission(self, request, view, obj):
#             return request.user == getattr(obj, self.attr)
#
#     return type("aaaa", (AppPermission,), {'attr': attr})
#

class DjangoModelPermissions(BasePermission):
    """
    The request is authenticated using `django.contrib.auth` permissions.
    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions

    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete` permissions on the model.

    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """

    # Map methods into required permission codes.
    # Override this if you need to also provide 'view' permissions,
    # or if you want to provide custom permission codes.
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        return [perm % kwargs for perm in self.perms_map[method]]

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # if request.user.is_superuser:
        #     return True
        return request.user.is_superuser or (request.user == obj)

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        queryset = view.get_queryset()
        perms = self.get_required_permissions(request.method, queryset.model)

        return request.user and request.user.has_perms(perms)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        return super().authenticate(request)

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        if len(auth) == 1:
            msg = ('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = ('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. '
                    'Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        if token in ['None', None, '']:
            msg = _('Empty token provided.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, key):
        try:
            # TODO(sax) add id/key matching
            token = ApiAuthToken.objects.get(token=key)
            user = token.user
            request.token = token
        except (User.DoesNotExist, ApiAuthToken.DoesNotExist):
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (user, key)

    # def authenticate_header(self, request):
    #     return self.keyword
