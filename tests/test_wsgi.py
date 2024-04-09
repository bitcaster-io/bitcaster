import pytest


def test_wsgi():
    try:
        from bitcaster.config.wsgi import application

        assert application.request_class
    except Exception as e:
        pytest.fail(e)



def test_asgi():
    try:
        from bitcaster.config.asgi import application

        assert application.request_class
    except Exception as e:
        pytest.fail(e)
