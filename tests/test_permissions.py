# -*- coding: utf-8 -*-
from unittest.mock import Mock

from mercury.permissions import TokenAuthentication


def test_tokenauthentication(rf, monkeypatch):
    t = TokenAuthentication()
    monkeypatch.setattr('mercury.permissions.ApiAuthToken', Mock())
    # request = rf.get('/')
    # assert t.authenticate(request) is None

    request = rf.get('/', HTTP_AUTHORIZATION='Token aaa')
    assert t.authenticate(request)
