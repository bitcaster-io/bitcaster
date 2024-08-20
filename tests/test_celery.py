import pytest


def test_celery() -> None:
    try:
        from bitcaster.config.celery import app

        assert app.clock
    except Exception as e:
        pytest.fail(getattr(e, "message", "unknown error"))


def test_init_celery() -> None:
    try:
        from bitcaster.config.celery import init_sentry

        init_sentry()
    except Exception as e:
        pytest.fail(getattr(e, "message", "unknown error"))
