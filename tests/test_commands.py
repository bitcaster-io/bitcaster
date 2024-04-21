import os
from io import StringIO
from unittest import mock

import pytest
from django.core.management import CommandError, call_command

pytestmark = pytest.mark.django_db


@pytest.fixture()
def environment():
    return {"CACHE_URL": "test", "CELERY_BROKER_URL": "", "DATABASE_URL": "", "SECRET_KEY": ""}


# @pytest.mark.parametrize(
#     "options",
#     [
#         {},
#         {"admin_email": "user@test.com", "admin_password": 123},
#     ],
# )
@pytest.mark.parametrize("verbosity", [1, 0], ids=["verbose", ""])
@pytest.mark.parametrize("migrate", [1, 0], ids=["migrate", ""])
def test_upgrade_init(verbosity, migrate, monkeypatch, environment):
    out = StringIO()
    # environ = {"CACHE_URL": "test", "CELERY_BROKER_URL": "", "DATABASE_URL": "", "SECRET_KEY": ""}
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command(
            "upgrade", admin_email="user@test.com", admin_password="123", stdout=out, check=False, verbosity=verbosity
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


def test_upgrade_check(mocked_responses, environment):
    out = StringIO()

    from testutils.factories import SuperUserFactory

    SuperUserFactory()

    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=True)


@pytest.mark.parametrize("verbosity", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("develop", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("diff", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("config", [0, 1], ids=["0", "1"])
@pytest.mark.parametrize("check", [0, 1], ids=["0", "1"])
def test_env(mocked_responses, verbosity, develop, diff, config, check):
    out = StringIO()
    environ = {"ADMIN_URL_PREFIX": "test"}
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
