import pytest

from bitcaster.utils.ttl import (DAY, HOUR, MINUTE, WEEK,
                                 YEAR, encode_ttl, parse_ttl,)

PARAMS = [('1s', 1), ('59s', 59), ('1m', MINUTE),
          ('1h', HOUR), ('1d', DAY), ('1w', WEEK), ('1y', YEAR),

          ('1m30s', 90), ('12h', 3600 * 12), ('3h30m', 12600),
          ]


@pytest.mark.parametrize('value,expected', PARAMS)
def test_parse_ttl(value, expected):
    assert parse_ttl(value) == expected


@pytest.mark.parametrize('arg,seconds', PARAMS)
def test_encode_ttl(arg, seconds):
    assert encode_ttl(seconds) == arg
