# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest

from bitcaster.api.permissions import TokenAuthentication


@pytest.mark.django_db
def test_tokenauthentication(rf, monkeypatch):
    t = TokenAuthentication()
    monkeypatch.setattr('bitcaster.api.permissions.ApiAuthToken', Mock())
    monkeypatch.setattr('bitcaster.api.permissions.ApiTriggerKey', Mock())
    monkeypatch.setattr('bitcaster.api.permissions.TokenAuthentication.model', Mock())
    monkeypatch.setattr('bitcaster.api.permissions.TriggerTokenAuthentication.model', Mock())
    # request = rf.get('/')
    # assert t.authenticate(request) is None

    request = rf.get('/', HTTP_AUTHORIZATION='Token aaa')
    assert t.authenticate(request)
