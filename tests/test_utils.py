# -*- coding: utf-8 -*-
import pytest

from bitcaster.utils.language import flatten, get_attr
from bitcaster.utils.net import NetList

values = ([1, 2, 3, 4, 5],
          [1, (2, 3), 4, 5],
          [1, (2, 3), (4, 5)],
          [(1, (2, 3), (4, 5))],
          )


@pytest.mark.parametrize('param', values, ids=list(map(str, values)))
def test_flatten(param):
    assert flatten(param) == [1, 2, 3, 4, 5]


def test_get_attr():
    class C(object):
        pass

    a = C()
    a.b = C()
    a.b.c = 4
    assert get_attr(a, 'b.c') == 4
    assert get_attr(a, 'b.c.y', None) is None


def test_netlist():
    ranges = NetList('10.0.0.0/24', '192.168.10.0/24')
    assert '192.168.10.1' in ranges
    assert '192.168.1.1' not in ranges

    ranges = NetList('0.0.0.0')
    ranges[0] = '10.0.0.0/8'
    assert '10.10.1.1' in ranges
    assert '192.168.1.1' not in ranges

    ranges = NetList('0.0.0.0/0')
    assert '1.1.1.1' in ranges
    assert '192.168.1.1' in ranges
