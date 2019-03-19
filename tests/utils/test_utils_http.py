import pytest
from constance.test import override_config


@override_config(SITE_URL='http://demo/')
@pytest.mark.parametrize('url', [None, '/abc/'])
def test_absolute_uri(url):
    from bitcaster.utils.http import absolute_uri
    assert absolute_uri(url)
