# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from mercury import logging

logger = logging.getLogger(__name__)


class IsAdministratorOrSameUser(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset
        # if not request.user.is_authenticated:
        #     return []
        return queryset.filter(id=request.user.pk)


class ApplicationOwnedFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        app = view.get_selected_application()
        if app:
            queryset = queryset.filter(application__id=app.pk)
        if request.user.is_superuser:
            return queryset
        if not request.user.is_authenticated:
            return []
        return queryset.filter(Q(application__organization__owner=request.user) |
                               Q(application__organization__members=request.user))


class IsOwnerFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user.is_authenticated:
            return queryset.none()
        app = view.get_selected_application()
        if app:
            return queryset.filter(id=app.pk)
        # else:
        if request.user.is_superuser:
            return queryset
        return queryset.filter(Q(organization__owner=request.user) |
                               Q(organization__members=request.user))


class MasterChildFilterBackend(BaseFilterBackend):
    lookup_field = None
    lookup_url_kwarg = None

    @classmethod
    def create(cls, lookup_field, lookup_url_kwarg):
        return type("-", (cls,), {'lookup_url_kwarg': lookup_url_kwarg,
                                  'lookup_field': lookup_field})

    def filter_queryset(self, request, queryset, view):
        lookup_url_kwarg = self.lookup_url_kwarg or view.parent_lookup_url_kwarg
        lookup_field = self.lookup_field or view.parent_lookup_field
        if lookup_url_kwarg in view.kwargs:
            return queryset.filter(**{lookup_field: view.kwargs[lookup_url_kwarg]})
        elif request.user.is_superuser:
            return queryset
        return queryset


class UserFilterBackend(MasterChildFilterBackend):
    lookup_url_kwarg = 'user__pk'
    lookup_field = 'user'


class ApplicationFilterBackend(MasterChildFilterBackend):
    lookup_url_kwarg = 'application__pk'
    lookup_field = 'application'
