from typing import TYPE_CHECKING

from django.test.client import RequestFactory
from user_agents.parsers import UserAgent

from bitcaster.utils.user_agent import (
    SmartUserAgent,
    get_cache_key,
    get_user_agent,
    parse,
)

if TYPE_CHECKING:
    from pytest import MonkeyPatch


CHROME = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/51.0.2704.103 Safari/537.36"
OPERA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
)
SAFARI = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"
)
IE = b"Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)"


def test_get_user_agent(rf: "RequestFactory") -> None:
    request = rf.get("/", HTTP_USER_AGENT=CHROME)
    ua = get_user_agent(request)
    assert ua.browser.family == "Chrome"
    assert ua.support_firebase
    assert not ua.is_safari
    assert not ua.is_ios


def test_get_cache_key() -> None:
    assert get_cache_key(b"aa") == get_cache_key("aa")


def test_parse() -> None:
    ua: SmartUserAgent = parse(OPERA)
    assert ua.browser.family == "Opera"


def test_safari(rf: "RequestFactory") -> None:
    request = rf.get("/", HTTP_USER_AGENT=SAFARI)
    ua = get_user_agent(request)
    assert ua.browser.family == "Mobile Safari"
    assert not ua.support_firebase
    assert ua.is_safari
    assert ua.is_ios


def test_bytes(rf: "RequestFactory") -> None:
    request = rf.get("/", HTTP_USER_AGENT=IE)
    ua = get_user_agent(request)
    assert ua.browser.family == "IE Mobile"
    assert not ua.is_safari
    assert ua.is_mobile


def test_cache(rf: "RequestFactory") -> None:
    request = rf.get("/", HTTP_USER_AGENT=IE)
    get_user_agent(request)
    ua = get_user_agent(request)
    assert ua.browser.family == "IE Mobile"
    assert not ua.is_safari
    assert ua.is_mobile


def test_no_cache(rf: "RequestFactory", monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr("bitcaster.utils.user_agent.cache", None)
    request = rf.get("/", HTTP_USER_AGENT=IE)
    ua: UserAgent = get_user_agent(request)
    assert ua.browser.family == "IE Mobile"
    assert not ua.is_safari
    assert ua.is_mobile
