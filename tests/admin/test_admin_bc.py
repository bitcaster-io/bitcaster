from typing import TYPE_CHECKING

from pytest_django.fixtures import SettingsWrapper

import pytest
from testutils.factories.user import UserFactory
from testutils.perms import user_grant_permissions

from django.contrib.admin.sites import site
from django.db.models import Model
from django.urls import reverse

if TYPE_CHECKING:
    from responses import RequestsMock

    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "app_label" in metafunc.fixturenames:
        m: dict[str, type[Model]] = {}
        for model in site._registry:
            m[model._meta.app_label] = model
        metafunc.parametrize("app_label,app_model", m.items(), ids=m.keys())


@pytest.fixture
def app(
    django_app_factory: "MixinWithInstanceVariables", mocked_responses: "RequestsMock", settings: SettingsWrapper
) -> "DjangoTestApp":
    settings.FLAGS = {"OLD_STYLE_UI": [("boolean", False)]}
    django_app = django_app_factory(csrf_checks=False)
    admin_user = UserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.mark.parametrize("can_change", [True, False], ids=("can_change", ""))
@pytest.mark.parametrize("can_add", [True, False], ids=("can_add", ""))
def test_admin_index(app: "DjangoTestApp", app_label: str, app_model: Model, can_change: bool, can_add: bool) -> None:
    perms = []
    if can_change:
        perms.append(f"{app_model._meta.app_label}.change_{app_model._meta.model_name}")
    if can_add:
        perms.append(f"{app_model._meta.app_label}.add_{app_model._meta.model_name}")
    with user_grant_permissions(app._user, perms, ignore_missing=True):
        url = reverse("admin:index")
        res = app.get(url)
    assert res.status_code == 200
