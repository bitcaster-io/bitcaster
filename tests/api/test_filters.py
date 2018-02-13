# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from django.contrib.auth.models import AnonymousUser
from unittest.mock import Mock

from tests_utils import override_threadlocals

from mercury.api.filters import ApplicationOwnedFilter, IsOwnerFilter
# from mercury.middleware import get_current_request, get_current_user
from mercury.models import Application, Event

logger = logging.getLogger(__name__)


def test_applicationownedfilter(rf, application1, event1, event2, admin):
    request = rf.get('/')
    request.user = AnonymousUser()

    f = ApplicationOwnedFilter()
    view = Mock(get_selected_application=lambda *a: application1)
    qs = Event.objects.all()

    with override_threadlocals(request=request):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == []

    with override_threadlocals(request=request, user=admin):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == [event1]

    with override_threadlocals(request=request, user=application1.owner):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == list(Event.objects.filter(application__owner=application1.owner))

    view = Mock(get_selected_application=lambda *a: None)

    with override_threadlocals(request=request, user=admin):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == list(qs)


def test_isownerfilter(rf, application1, application2, admin):
    request = rf.get('/')
    request.user = AnonymousUser()
    f = IsOwnerFilter()

    view = Mock(get_selected_application=lambda *a: application1)

    qs = Application.objects.all()
    with override_threadlocals(request=request):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == []

    with override_threadlocals(request=request, user=admin):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == [application1]

    with override_threadlocals(request=request, user=application1.owner):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == list(Application.objects.filter(owner=application1.owner))

    view = Mock(get_selected_application=lambda *a: None)

    with override_threadlocals(request=request, user=admin):
        result = f.filter_queryset(request, qs, view)
        assert list(result) == list(qs)
