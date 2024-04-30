import pytest
from django.http import HttpResponse
from freezegun import freeze_time

from bitcaster.state import State


@pytest.fixture
def state():
    s = State()
    s.reset()
    return s


def test_state(state):
    assert not state.request


def test_cookies(state):

    assert not state.cookies


def test_configure(state):
    with state.configure(a=1):
        assert state.a == 1
        with state.configure(request=1, not_set=2):
            assert state.request == 1
            assert state.not_set == 2
            assert state.a == 1
        assert state.request is None
        assert not hasattr(state, "not_set")


@freeze_time("2000-01-01T00:00:00Z")
def test_add_cookies(state):
    state.add_cookie("test", 22, 3600, None, "/path/", "domain.example.com", True, True, "lax")
    r: HttpResponse = HttpResponse()
    state.set_cookies(r)

    assert dict(list(r.cookies.values())[0]) == {
        "comment": "",
        "domain": "domain.example.com",
        "expires": "Sat, 01 Jan 2000 01:00:00 GMT",
        "httponly": True,
        "max-age": 3600,
        "path": "/path/",
        "samesite": "lax",
        "secure": True,
        "version": "",
    }
