# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from bitcaster.api.permissions import (CsrfExemptSessionAuthentication,
                                       IsApplicationRelated,
                                       IsOwnerOrMaintainter,
                                       TokenAuthentication,
                                       TokenAuthenticationBase,
                                       TriggerTokenAuthentication,)


@pytest.mark.django_db
def test_csrfexemptsessionauthentication(organization1, organization2):
    t = CsrfExemptSessionAuthentication()
    request = Mock(_request=APIRequestFactory(enforce_csrf_checks=True).get('/'))
    assert not t.authenticate(request)

    request._request.user = Mock(active=True)
    assert t.authenticate(request) == (request._request.user, None)


@pytest.mark.django_db
def test_tokenauthenticationbase(rf, monkeypatch):
    t = TokenAuthenticationBase()
    request = rf.get('/')
    assert not t.authenticate(request)

    request = rf.get('/', HTTP_AUTHORIZATION='')
    assert not t.authenticate(request)

    with pytest.raises(AuthenticationFailed):
        request = rf.get('/', HTTP_AUTHORIZATION='Token')
        t.authenticate(request)

    with pytest.raises(AuthenticationFailed):
        request = rf.get('/', HTTP_AUTHORIZATION='Token aa bb')
        t.authenticate(request)

    with pytest.raises(AuthenticationFailed):
        request = rf.get('/', HTTP_AUTHORIZATION='Token àî')
        t.authenticate(request)

    with pytest.raises(AuthenticationFailed):
        request = rf.get('/', HTTP_AUTHORIZATION='Token None')
        t.authenticate(request)

    t.model = Mock(objects=Mock(get=lambda *a, **k: Mock(user=Mock(is_active=False))))
    with pytest.raises(AuthenticationFailed):
        request = rf.get('/', HTTP_AUTHORIZATION='Token abc')
        t.authenticate(request)


@pytest.mark.django_db
def test_tokenauthentication(rf, application1, user1):
    t = TokenAuthentication()
    token = user1.add_token(application=application1)
    request = rf.get('/', HTTP_AUTHORIZATION=f'Token {token.token}')
    assert t.authenticate(request)

    with pytest.raises(AuthenticationFailed):
        request = rf.get('/', HTTP_AUTHORIZATION=f'Token abc')
        assert t.authenticate(request)


@pytest.mark.django_db
def test_triggertokenauthentication(rf, application1, user1):
    t = TriggerTokenAuthentication()
    token = user1.add_trigger(application=application1)
    request = rf.get('/', HTTP_AUTHORIZATION=f'Token {token.token}')
    assert t.authenticate(request)


@pytest.mark.django_db
def test_isownerormaintainter(rf, organization1, organization2):
    request = rf.get('/')
    request.user = organization1.owner
    perm = IsOwnerOrMaintainter()
    assert perm.has_permission(request, Mock())

    assert perm.has_object_permission(request,
                                      Mock(),
                                      organization1)
    assert not perm.has_object_permission(request,
                                          Mock(),
                                          organization2)


@pytest.mark.django_db
def test_isapplicationrelated(rf, event1, event2):
    request = rf.get('/')
    view1 = Mock(get_selected_application=lambda: event1.application)
    view2 = Mock(get_selected_application=lambda: event2.application)
    request.user = event1.application.organization.owner
    perm = IsApplicationRelated()

    assert perm.has_permission(request, view1)
    assert not perm.has_permission(request, view2)

    assert perm.has_object_permission(request,
                                      view1,
                                      event1)
    assert not perm.has_object_permission(request,
                                          view2,
                                          event2)
