from typing import TYPE_CHECKING, Any

import pytest
from django.urls import reverse
from pytest_django.fixtures import DjangoAssertNumQueries, SettingsWrapper
from responses import RequestsMock
from testutils.factories.user import SuperUserFactory

from bitcaster.state import state

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture()
def data() -> None:
    from testutils.factories import OccurrenceFactory

    OccurrenceFactory()


@pytest.fixture()
def app(
    django_app_factory: "MixinWithInstanceVariables", mocked_responses: "RequestsMock", settings: SettingsWrapper
) -> "DjangoTestApp":
    settings.FLAGS = {"OLD_STYLE_UI": [("boolean", True)]}
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_admin_index(app: "DjangoTestApp", data: Any, django_assert_num_queries: DjangoAssertNumQueries) -> None:
    url = reverse("admin:index")
    with django_assert_num_queries(16):
        res = app.get(url)
        assert res.status_code == 200
    state.reset()
    with django_assert_num_queries(14):
        res = app.get(url)
        assert res.status_code == 200
