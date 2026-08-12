# mypy: disable-error-code="attr-defined"
from typing import TYPE_CHECKING

import pytest
from testutils.factories import ApplicationFactory, ApplicationMembershipFactory
from testutils.factories.user import SuperUserFactory

from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

pytestmark = [pytest.mark.admin, pytest.mark.django_db]

HELP_SITE = "https://docs.bitcaster.io"


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_admin_index_contains_link(app: "DjangoTestApp") -> None:
    res = app.get(reverse("admin:index"))
    assert res.status_code == 200
    assert f'href="{HELP_SITE}/adm-guide/quickstart/"' in res


def test_admin_changelist_contains_link(app: "DjangoTestApp") -> None:
    ApplicationFactory()
    res = app.get(reverse("admin:bitcaster_application_changelist"))
    assert res.status_code == 200
    assert f'href="{HELP_SITE}/adm-guide/app/"' in res


def test_admin_change_form_contains_link(app: "DjangoTestApp") -> None:
    application = ApplicationFactory()
    res = app.get(reverse("admin:bitcaster_application_change", args=[application.pk]))
    assert res.status_code == 200
    assert f'href="{HELP_SITE}/adm-guide/app/"' in res


def test_admin_membership_changelist_contains_link(app: "DjangoTestApp") -> None:
    ApplicationMembershipFactory()
    res = app.get(reverse("admin:bitcaster_applicationmembership_changelist"))
    assert res.status_code == 200
    assert f'href="{HELP_SITE}/adm-guide/membership/"' in res


def test_admin_membership_change_form_contains_link(app: "DjangoTestApp") -> None:
    membership = ApplicationMembershipFactory()
    res = app.get(reverse("admin:bitcaster_applicationmembership_change", args=[membership.pk]))
    assert res.status_code == 200
    assert f'href="{HELP_SITE}/adm-guide/membership/"' in res


def test_admin_popup_has_no_link(app: "DjangoTestApp") -> None:
    application = ApplicationFactory()
    res = app.get(reverse("admin:bitcaster_application_change", args=[application.pk]) + "?_popup=1")
    assert res.status_code == 200
    assert f'href="{HELP_SITE}' not in res


def test_console_contains_link(app: "DjangoTestApp") -> None:
    res = app.get(reverse("console:index"))
    assert res.status_code == 200
    assert f'href="{HELP_SITE}/adm-guide/cli/"' in res
