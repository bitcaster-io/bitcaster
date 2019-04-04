
from bitcaster.utils.net import NetList


def test_contains():
    net = NetList('192.168.10.0/24')
    assert '192.168.10.1' in net
    assert '192.168.11.1' not in net


def test_setitem():
    net = NetList('192.168.10.0/24')
    net[0] = '192.168.10.1'


def test_getitem():
    net = NetList('192.168.10.0/24')
    assert net[0]


def test_iter():
    net = NetList('192.168.10.0/24')
    for i in net:
        assert i
