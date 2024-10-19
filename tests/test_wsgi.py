import pytest


def test_wsgi() -> None:
    try:
        from bitcaster.config.wsgi import application

        assert application.request_class
    except Exception as e:
        pytest.fail(str(e))


def test_asgi() -> None:
    try:
        from bitcaster.config.asgi import application

        assert application.request_class
    except Exception as e:
        pytest.fail(str(e))
