from rest_framework import permissions, authentication


class ApiKeyAuthentication(authentication.TokenAuthentication):
    pass


class TriggerPermission(permissions.BasePermission):
    pass
