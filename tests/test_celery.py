import pytest


def test_celery():
    try:
        from bitcaster.config.celery import app

        assert app.clock
    except Exception as e:
        pytest.fail(getattr(e, "message", "unknown error"))


def test_init_celery():
    try:
        from bitcaster.config.celery import init_sentry

        assert init_sentry()
    except Exception as e:
        pytest.fail(getattr(e, "message", "unknown error"))
