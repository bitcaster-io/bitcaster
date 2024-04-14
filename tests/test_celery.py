import pytest


def test_celery():
    try:
        from bitcaster.config.celery import app

        assert app.clock
    except Exception as e:
        pytest.fail(getattr(e, "message", "unknown error"))
