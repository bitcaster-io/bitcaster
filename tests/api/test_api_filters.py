# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import AnonymousUser

from bitcaster.api.filters import ApplicationFilterBackend, IsOwnerFilter
from bitcaster.models import Application, Event


@pytest.mark.django_db
def test_isownerfilter(rf, application1, application2, admin):
    queryset = Application.objects.all()
    request = rf.get('/')
    f = IsOwnerFilter()

    request.user = application1.organization.owner
    ret = f.filter_queryset(request, queryset, None).values_list('pk',
                                                                 flat=True)
    assert list(ret) == [application1.pk]

    request.user = admin
    ret = f.filter_queryset(request, queryset, None).values_list('pk',
                                                                 flat=True)
    assert list(ret) == list(queryset.values_list('pk', flat=True))


@pytest.mark.django_db
def test_userfilterbackend(rf, application1, application2, admin):
    pass


@pytest.mark.django_db
def test_applicationfilterbackend(rf, event1, event2, admin):
    application = event1.application
    queryset = Event.objects.all()
    request = rf.get(f'/{application.organization.slug}/')
    view = Mock(kwargs={ApplicationFilterBackend.lookup_url_kwarg: application.pk})
    f = ApplicationFilterBackend()

    ret = f.filter_queryset(request, queryset, view).values_list('pk', flat=True)
    assert list(ret) == [event1.pk]

    view = Mock(kwargs={})
    request.user = AnonymousUser()
    ret = f.filter_queryset(request, queryset, view).values_list('pk', flat=True)
    assert list(ret) == list(queryset.values_list('pk', flat=True))

    request.user = admin
    view = Mock(kwargs={})
    ret = f.filter_queryset(request, queryset, view).values_list('pk', flat=True)
    assert list(ret) == list(queryset.values_list('pk', flat=True))
