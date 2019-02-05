from bitcaster.dispatchers import SystemEmail


def test_systememail():
    s = SystemEmail()
    assert s._get_connection()
