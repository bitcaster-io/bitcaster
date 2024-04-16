from unittest.mock import Mock

from bitcaster.utils.security import is_root


def test_is_root(rf, settings):
    request = rf.get("/")
    request.user = Mock()
    assert not is_root(request)
    settings.ROOT_TOKEN = "aaa"
    request = rf.get("/", **{f"HTTP_{settings.ROOT_TOKEN_HEADER}": "aaa"})
    request.user = Mock()
    assert is_root(request)
