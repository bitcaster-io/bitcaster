import os
from io import StringIO
from unittest import mock

import pytest
from django.core.management import CommandError, call_command
from testutils.factories import SuperUserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def environment():
    return {
        "CACHE_URL": "test",
        "CELERY_BROKER_URL": "",
        "DATABASE_URL": "",
        "SECRET_KEY": "",
        "MEDIA_ROOT": "/tmp/media",
        "STATIC_ROOT": "/tmp/static",
        "SECURE_SSL_REDIRECT": "1",
        "SESSION_COOKIE_SECURE": "1",
    }


@pytest.mark.parametrize("static_root", ["static", ""], ids=["static_missing", "static_existing"])
@pytest.mark.parametrize("static", [True, False], ids=["static", "no-static"])
@pytest.mark.parametrize("verbosity", [1, 0], ids=["verbose", ""])
@pytest.mark.parametrize("migrate", [True, False], ids=["migrate", ""])
def test_upgrade_init(verbosity, migrate, monkeypatch, environment, static, static_root, tmp_path):
    static_root_path = tmp_path / static_root
    out = StringIO()
    with mock.patch.dict(os.environ, {**environment, "STATIC_ROOT": str(static_root_path.absolute())}, clear=True):
        call_command(
            "upgrade",
            static=static,
            admin_email="user@test.com",
            admin_password="123",
            migrate=migrate,
            stdout=out,
            check=False,
            verbosity=verbosity,
        )
    assert "error" not in str(out.getvalue())


@pytest.mark.parametrize("verbosity", [1, 0], ids=["verbose", ""])
@pytest.mark.parametrize("migrate", [1, 0], ids=["migrate", ""])
def test_upgrade(verbosity, migrate, monkeypatch, environment):
    from testutils.factories import SuperUserFactory

    out = StringIO()
    SuperUserFactory()
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=False, verbosity=verbosity)
    assert "error" not in str(out.getvalue())


def test_upgrade_check(mocked_responses, admin_user, environment):
    out = StringIO()
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=True)


def test_upgrade_noadmin(transactional_db, mocked_responses, environment):
    out = StringIO()
    with mock.patch.dict(os.environ, environment, clear=True):
        with pytest.raises(SystemExit):
            call_command("upgrade", stdout=out, check=True, admin_email="")


@pytest.mark.parametrize("admin", [True, False], ids=["existing_admin", "new_admin"])
def test_upgrade_admin(transactional_db, mocked_responses, environment, admin):
    if admin:
        email = SuperUserFactory().email
    else:
        email = "new-@example.com"

    out = StringIO()
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=True, admin_email=email)


@pytest.mark.parametrize("verbosity", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("develop", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("diff", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("config", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("check", [0, 1], ids=["0", "1"])
def test_env(mocked_responses, verbosity, develop, diff, config, check):
    out = StringIO()
    environ = {
        "ADMIN_URL_PREFIX": "test",
        "SECURE_SSL_REDIRECT": "1",
        "SECRET_KEY": "a" * 120,
        "SESSION_COOKIE_SECURE": "1",
    }
    with mock.patch.dict(os.environ, environ, clear=True):
        call_command(
            "env",
            ignore_errors=True if check == 1 else False,
            stdout=out,
            verbosity=verbosity,
            develop=develop,
            diff=diff,
            config=config,
            check=check,
        )
        assert "error" not in str(out.getvalue())


def test_env_raise(mocked_responses):
    environ = {"ADMIN_URL_PREFIX": "test"}
    with mock.patch.dict(os.environ, environ, clear=True):
        with pytest.raises(CommandError):
            call_command("env", ignore_errors=False, check=True)
