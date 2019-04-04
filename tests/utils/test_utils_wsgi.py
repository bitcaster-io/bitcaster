
from bitcaster.utils.wsgi import get_client_ip


def test_get_client_ip(rf):
    assert get_client_ip(rf.get('/'))
