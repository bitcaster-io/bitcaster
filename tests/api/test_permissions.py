# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from rest_framework.exceptions import AuthenticationFailed

from bitcaster.api.permissions import (IsOwnerOrMaintainter,
                                       TokenAuthentication,
                                       TokenAuthenticationBase,
                                       TriggerTokenAuthentication,)


@pytest.mark.django_db
def test_tokenauthenticationbase(rf, monkeypatch):
    t = TokenAuthenticationBase()
    monkeypatch.setattr('bitcaster.api.permissions.ApiAuthToken', Mock())
    monkeypatch.setattr('bitcaster.api.permissions.ApiTriggerKey', Mock())
    monkeypatch.setattr('bitcaster.api.permissions.TokenAuthentication.model', Mock())
    monkeypatch.setattr('bitcaster.api.permissions.TriggerTokenAuthentication.model', Mock())

    # request = rf.get('/')
    # assert not t.authenticate(request)

    # with pytest.raises(AuthenticationFailed):
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

    #
    # request = rf.get('/', HTTP_AUTHORIZATION='Token aaa')
    # assert t.authenticate(request)
    #
    # request = rf.get('/', HTTP_AUTHORIZATION='Token aaa')
    # assert t.authenticate(request)


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
    assert perm.has_object_permission(request,
                                      Mock(),
                                      organization1)
    assert not perm.has_object_permission(request,
                                      Mock(),
                                      organization2)
