from typing import TYPE_CHECKING

import os
import random
from io import StringIO
from pathlib import Path

from responses import RequestsMock

import pytest
from unittest import mock

from django.core.management import CommandError, call_command

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper

    from bitcaster.models import Application, Organization, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def environment() -> dict[str, str]:
    return {
        "CACHE_URL": "test",
        "DRAMATIQ_BROKER": "",
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
def test_upgrade_init(
    verbosity: int,
    migrate: bool,
    monkeypatch: pytest.MonkeyPatch,
    environment: dict[str, str],
    static: bool,
    static_root: str,
    tmp_path: Path,
    settings: "SettingsWrapper",
) -> None:
    if static_root:
        static_root_path = tmp_path / static_root
        static_root_path.mkdir()
    else:
        static_root_path = tmp_path / str(random.randint(1, 10000))
        assert not Path(static_root_path).exists()
    out = StringIO()
    settings.STATIC_ROOT = str(static_root_path.absolute())
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
def test_upgrade(verbosity: int, migrate: int, monkeypatch: pytest.MonkeyPatch, environment: dict[str, str]) -> None:
    from testutils.factories import SuperUserFactory

    out = StringIO()
    SuperUserFactory()
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=False, verbosity=verbosity)
    assert "error" not in str(out.getvalue())


def test_upgrade_multi_superuser(environment: dict[str, str]) -> None:
    from testutils.factories import OrganizationFactory, SuperUserFactory

    from bitcaster.constants import bitcaster

    owner = SuperUserFactory()
    OrganizationFactory(name=bitcaster.ORGANIZATION, slug=bitcaster.ORGANIZATION.lower(), owner=owner)
    SuperUserFactory()
    out = StringIO()
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=False)
    assert "error" not in str(out.getvalue())


def test_upgrade_next(mocked_responses: RequestsMock) -> None:
    from testutils.factories import ProjectFactory, SuperUserFactory

    SuperUserFactory()
    ProjectFactory()
    out = StringIO()
    call_command("upgrade", stdout=out, check=False)
    assert "error" not in str(out.getvalue())


def test_upgrade_check(mocked_responses: RequestsMock, admin_user: "User", environment: dict[str, str]) -> None:
    out = StringIO()
    with mock.patch.dict(os.environ, environment, clear=True):
        call_command("upgrade", stdout=out, check=True)


@pytest.mark.django_db(transaction=True)
def test_upgrade_noadmin(mocked_responses: RequestsMock, environment: dict[str, str]) -> None:
    out = StringIO()
    with mock.patch.dict(os.environ, environment, clear=True):
        with pytest.raises(SystemExit):
            call_command("upgrade", stdout=out, check=True, admin_email="")


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("admin", [True, False], ids=["existing_admin", "new_admin"])
def test_upgrade_admin(mocked_responses: RequestsMock, environment: dict[str, str], admin: str) -> None:
    from testutils.factories import SuperUserFactory

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
def test_env(mocked_responses: RequestsMock, verbosity: int, develop: int, diff: int, config: int, check: int) -> None:
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
            ignore_errors=check == 1,
            stdout=out,
            verbosity=verbosity,
            develop=develop,
            diff=diff,
            config=config,
            check=check,
        )
        assert "error" not in str(out.getvalue())


def test_env_raise(mocked_responses: RequestsMock) -> None:
    environ = {"ADMIN_URL_PREFIX": "test"}
    with mock.patch.dict(os.environ, environ, clear=True):
        with pytest.raises(CommandError):
            call_command("env", ignore_errors=False, check=True)


def test_develop_quickstart(bitcaster: "Application") -> None:
    from bitcaster.models import (
        Address,
        Assignment,
        Channel,
        MessageTemplate,
        Notification,
        Organization,
        Project,
        Subscription,
    )
    from bitcaster.models.choices import FILTERING_SUBSCRIPTION

    out = StringIO()
    structure = "user@example.com;Org;Project1;Application1"
    with mock.patch.dict(os.environ, {"TEST_ORG_STRUCTURE": structure, "TEST_API_KEY": "test-key"}, clear=False):
        call_command("develop", stdout=out, verbosity=1)

    assert Organization.objects.filter(name="Org").exists()
    assert Project.objects.filter(name="Project1").exists()
    assert Channel.objects.filter(project__name="Project1").exists()
    assert Notification.objects.filter(event__name="Test Event", policy=FILTERING_SUBSCRIPTION, active=True).exists()
    assert MessageTemplate.objects.filter(notification__name="Default").exists()
    assert Address.objects.filter(user__username="user@example.com").exists()
    assert Assignment.objects.filter(validated=True, active=True).exists()
    assert Subscription.objects.filter(notification__name="Default", active=True).exists()
    assert "Created/Updated Subscription" in out.getvalue()


def test_develop_quickstart_reuse_local_org(bitcaster: "Application", organization: "Organization") -> None:
    from bitcaster.models import Organization, Project

    out = StringIO()
    structure = "user@example.com;Org;Project1;Application1"
    with mock.patch.dict(os.environ, {"TEST_ORG_STRUCTURE": structure}, clear=False):
        call_command("develop", stdout=out, verbosity=1)

    assert Organization.objects.count() <= 2
    assert Project.objects.filter(name="Project1").exists()
    assert "Created/Updated Subscription" in out.getvalue()
