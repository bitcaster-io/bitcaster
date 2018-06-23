# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from constance.test import override_config
from django.http import HttpResponse
from django.test import RequestFactory

pytestmark = pytest.mark.django_db


@override_config(INITIALIZED=False)
def test_setupmiddleware_not_initialized():
    from bitcaster.middleware.setup import SetupMiddleware
    request = RequestFactory().get('/')
    middleware = SetupMiddleware(Mock())
    response = middleware(request)
    assert response.status_code == 302
    assert response.url == '/setup/'


@override_config(INITIALIZED=True)
def test_setupmiddleware_initialized():
    from bitcaster.middleware.setup import SetupMiddleware
    request = RequestFactory().get('/')
    middleware = SetupMiddleware(Mock(return_value=HttpResponse()))
    response = middleware(request)
    assert response.status_code == 200


def test_envmiddleware():
    from bitcaster.state import state
    from bitcaster.middleware.env import BitcasterEnvMiddleware
    request = RequestFactory().get('/')
    middleware = BitcasterEnvMiddleware(Mock(return_value=HttpResponse()))
    response = middleware(request)
    assert response.status_code == 200
    assert state.request == request


def test_securitymiddleware():
    from bitcaster.middleware.security import SecurityHeadersMiddleware
    request = RequestFactory().get('/')
    middleware = SecurityHeadersMiddleware(Mock(return_value=HttpResponse()))
    response = middleware(request)
    assert response.status_code == 200
    assert 'X-Frame-Options' in response
    assert 'X-Content-Type-Options' in response
    assert 'X-XSS-Protection' in response
