from constance.test import override_config

import bitcaster
from bitcaster.web.templatetags.bc_assets import aasset, asset, aurl


def test_asset():
    assert bitcaster.get_full_version() in asset('/')


@override_config(SITE_URL='http://demo/')
def test_aasset():
    assert aasset('/').startswith('http')


@override_config(SITE_URL='http://demo/')
def test_aurl():
    assert aurl('index').startswith('http')
