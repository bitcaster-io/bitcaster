from typing import TYPE_CHECKING, Generator

import os

from flags.state import disable_flag, enable_flag
from seleniumbase import config as sb_config

import pytest
from testutils.liveserver import WatchingLiveServer, static_404s
from testutils.selenium import TestBrowser

if TYPE_CHECKING:
    from bitcaster.state import State


@pytest.fixture(scope="session")
def live_server(request) -> "Generator[WatchingLiveServer, None, None]":
    addr = request.config.getvalue("liveserver") or os.getenv("DJANGO_LIVE_TEST_SERVER_ADDRESS") or "localhost"
    server = WatchingLiveServer(addr)
    yield server
    server.stop()


@pytest.fixture
def mock_state(rf) -> "Generator[State, None, None]":
    from bitcaster.state import state

    state.request = rf.get("/")
    yield state
    state.request = None


@pytest.fixture
def browser(live_server, request) -> "Generator[TestBrowser, None, None]":
    """SeleniumBase as a pytest fixture.
    Usage example: "def test_one(sb):"
    You may need to use this for tests that use other pytest fixtures."""
    enable_flag("LOCAL_LOGIN")
    static_404s.clear()
    sb = TestBrowser("base_method")
    sb.live_server_url = str(live_server)
    sb.setUp()
    sb._needs_tearDown = True
    sb._using_sb_fixture = True
    sb._using_sb_fixture_no_class = True
    sb_config._sb_node[request.node.nodeid] = sb
    sb.set_window_size(3000, 2000)
    sb.maximize_window()
    yield sb
    disable_flag("LOCAL_LOGIN")
    if sb._needs_tearDown:
        sb.tearDown()
        sb._needs_tearDown = False
    if static_404s:
        pytest.fail(f"Static resource(s) returned 404: {sorted(static_404s)}")
